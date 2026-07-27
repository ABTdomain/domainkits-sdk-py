from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_BASE_URL = "https://premium-api.domainkits.com/api/v1"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 2


@dataclass
class RateLimit:
    limit: int | None
    remaining: int | None
    reset_at: datetime | None


class DomainKitsError(Exception):
    def __init__(self, message: str, status: int, rate_limit: RateLimit):
        super().__init__(message)
        self.status = status
        self.rate_limit = rate_limit


class RateLimitError(DomainKitsError):
    def __init__(self, message: str, rate_limit: RateLimit):
        super().__init__(message, 429, rate_limit)

    @property
    def retry_after_ms(self) -> int | None:
        if not self.rate_limit.reset_at:
            return None
        delta = (self.rate_limit.reset_at - datetime.now(timezone.utc)).total_seconds() * 1000
        return max(0, int(delta))


class AuthError(DomainKitsError):
    pass


def _read_rate_limit(headers: Any) -> RateLimit:
    def num(name: str) -> int | None:
        raw = headers.get(name)
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError:
            return None

    reset = num("x-ratelimit-reset")
    return RateLimit(
        limit=num("x-ratelimit-limit"),
        remaining=num("x-ratelimit-remaining"),
        reset_at=datetime.fromtimestamp(reset, tz=timezone.utc) if reset is not None else None,
    )


def _extract_error(body: bytes) -> str | None:
    try:
        parsed = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    error = parsed.get("error") if isinstance(parsed, dict) else None
    return error if isinstance(error, str) else None


def _backoff_seconds(error: RateLimitError, attempt: int) -> float | None:
    until_ms = error.retry_after_ms
    if until_ms is None:
        return float(2**attempt)
    if until_ms > 120_000:
        return None
    return until_ms / 1000 + 0.25


class DomainKitsClient:
    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        if not api_key:
            raise ValueError("api_key is required. The DomainKits REST API rejects unauthenticated requests.")
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def request_raw(self, path: str, params: dict[str, Any] | None = None) -> tuple[int, Any, bytes]:
        query: dict[str, str] = {}
        for key, value in (params or {}).items():
            if value is None or value == "":
                continue
            if isinstance(value, bool):
                query[key] = "true" if value else "false"
            elif isinstance(value, (list, tuple)):
                query[key] = ",".join(str(v) for v in value)
            else:
                query[key] = str(value)
        url = self.base_url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)

        last_error: DomainKitsError | None = None
        for attempt in range(self.max_retries + 1):
            request = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                    "User-Agent": "domainkits-python/0.1.0",
                },
            )
            try:
                response = urllib.request.urlopen(request, timeout=self.timeout)
                return response.status, response.headers, response.read()
            except urllib.error.HTTPError as e:
                body = e.read()
                rate_limit = _read_rate_limit(e.headers)
                message = _extract_error(body) or f"Request failed with status {e.code}"

                if e.code in (401, 403):
                    raise AuthError(message, e.code, rate_limit) from None

                if e.code == 429:
                    rate_error = RateLimitError(message, rate_limit)
                    last_error = rate_error
                    wait = _backoff_seconds(rate_error, attempt)
                    if attempt < self.max_retries and wait is not None:
                        time.sleep(wait)
                        continue
                    raise rate_error from None

                if e.code >= 500 and attempt < self.max_retries:
                    last_error = DomainKitsError(message, e.code, rate_limit)
                    time.sleep(0.5 * (2**attempt))
                    continue

                raise DomainKitsError(message, e.code, rate_limit) from None

        raise last_error if last_error else DomainKitsError(
            "Request failed after retries", 0, RateLimit(None, None, None)
        )

    def _parse(self, path: str, params: dict[str, Any] | None) -> tuple[Any, int, Any]:
        status, headers, body = self.request_raw(path, params)
        envelope = json.loads(body)
        if isinstance(envelope, dict) and envelope.get("success") is False:
            raise DomainKitsError(
                envelope.get("error") or "DomainKits API returned an error",
                status,
                _read_rate_limit(headers),
            )
        return envelope, status, headers

    def request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        envelope, _, _ = self._parse(path, params)
        if isinstance(envelope, dict) and envelope.get("data") is not None:
            return envelope["data"]
        return envelope

    def request_list(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        envelope, _, _ = self._parse(path, params)
        data = envelope.get("data") if isinstance(envelope, dict) else None
        if not isinstance(data, list):
            data = []
        total = envelope.get("total") if isinstance(envelope, dict) else None
        return {"data": data, "total": total if isinstance(total, int) else len(data)}

    def request_envelope(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        envelope, _, _ = self._parse(path, params)
        return envelope

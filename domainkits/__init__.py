from __future__ import annotations

from typing import Any, Iterator

from .client import (
    AuthError,
    DomainKitsClient,
    DomainKitsError,
    RateLimit,
    RateLimitError,
)

__version__ = "0.3.8"
__all__ = [
    "DomainKits",
    "DomainKitsError",
    "RateLimitError",
    "AuthError",
    "RateLimit",
    "SearchResource",
]

MAX_LIMIT = 500


class SearchResource:
    def __init__(self, client: DomainKitsClient, path: str):
        self._client = client
        self._path = path

    def list(self, **params: Any) -> dict[str, Any]:
        return self._client.request_list(self._path, params)

    def paginate(self, page_size: int = MAX_LIMIT, **params: Any) -> Iterator[dict[str, Any]]:
        offset = int(params.pop("offset", 0) or 0)
        limit = min(page_size, MAX_LIMIT)
        while True:
            result = self._client.request_list(self._path, {**params, "limit": limit, "offset": offset})
            data = result["data"]
            yield from data
            offset += len(data)
            if not data or offset >= result["total"]:
                return

    def export(self, **params: Any) -> str:
        _, _, body = self._client.request_raw(self._path, {**params, "export": "csv"})
        return body.decode("utf-8")


class DomainKits:
    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 2,
    ):
        self._client = DomainKitsClient(api_key, base_url=base_url, timeout=timeout, max_retries=max_retries)

        self.expired = SearchResource(self._client, "/search/expired")
        self.nrds = SearchResource(self._client, "/search/nrds")
        self.nrds_live = SearchResource(self._client, "/search/nrds-live")
        self.aged = SearchResource(self._client, "/search/aged")
        self.active = SearchResource(self._client, "/search/active")
        self.deleted = SearchResource(self._client, "/search/deleted")
        self.market = SearchResource(self._client, "/search/market")

    def usage(self) -> dict[str, Any]:
        return self._client.request("/usage")

    def search_status(self) -> dict[str, Any]:
        return self._client.request("/search/status")

    def health(self) -> dict[str, Any]:
        return self._client.request_envelope("/health")

    def whois(self, domain: str) -> dict[str, Any]:
        return self._client.request("/whois", {"domain": domain})

    def dns(self, domain: str) -> dict[str, Any]:
        return self._client.request("/dns", {"domain": domain})

    def bulk_dns(self, domains: list[str]) -> dict[str, Any]:
        return self._client.request_bulk("/bulk/dns", {"domains": domains})

    def bulk_whois(self, domains: list[str]) -> dict[str, Any]:
        return self._client.request_bulk("/bulk/whois", {"domains": domains})

    def safety(self, domain: str) -> dict[str, Any]:
        return self._client.request("/safety", {"domain": domain})

    def ip_lookup(self, query: str) -> dict[str, Any] | None:
        result = self._client.request_list("/ip-lookup", {"query": query})
        data = result["data"]
        return data[0] if data else None

    def registrar(self, query: str, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/registrar", {"query": query, **params})

    def status_guide(self, query: str | None = None) -> dict[str, Any]:
        return self._client.request_list("/status-guide", {"query": query})

    def tld_check(self, prefix: str, **params: Any) -> dict[str, Any]:
        return self._client.request_envelope("/tld-check", {"prefix": prefix, **params})

    def ns_reverse(self, ns: str, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/ns-reverse", {"ns": ns, **params})

    def typosquat(self, domain: str, **params: Any) -> dict[str, Any]:
        return self._client.request_envelope("/typosquat", {"domain": domain, **params})

    def monitor_changes(self, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/monitor/changes", params)

    def ct_subdomains(self, domain: str, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/ct/subdomains", {"domain": domain, **params})

    def ct_certs(self, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/ct/certs", params)

    def ct_search(self, keyword: str, **params: Any) -> dict[str, Any]:
        return self._client.request_list("/ct/search", {"keyword": keyword, **params})

    def tld_trends(self, type: str, **params: Any) -> Any:
        return self._client.request(f"/trends/tlds/{type}", params)

    def keyword_trends(self, type: str, **params: Any) -> Any:
        return self._client.request(f"/trends/keywords/{type}", params)

    def nrds_download(self, **params: Any) -> bytes:
        _, _, body = self._client.request_raw("/nrds/download", params)
        return body

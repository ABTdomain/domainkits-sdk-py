# domainkits

Python client for the [DomainKits](https://domainkits.com) REST API.

This is the official Python SDK for the DomainKits API, published and maintained by the DomainKits team. DomainKits is built and operated by Lyalpha GmbH, with domain data and infrastructure provided by [ABTdomain](https://abtdomain.com), our domain intelligence and data aggregation platform. This repository is hosted under the ABTdomain GitHub organisation. Learn more about the relationship at [domainkits.com/about](https://domainkits.com/about).

Every parameter, response field and current limit is documented in the [API reference](https://domainkits.com/dev/api-docs) and the [OpenAPI spec](https://domainkits.com/dev/openapi.yaml). This README only lists what the SDK covers. No dependencies outside the standard library.

## Requirements

The REST API is for Premium and Platinum accounts; unauthenticated requests are rejected with 401. Keys start with `dk_` and come from [domainkits.com](https://domainkits.com/pricing).

## Install

```bash
pip install domainkits
```

## Usage

```python
import os
from domainkits import DomainKits

dk = DomainKits(os.environ["DOMAINKITS_API_KEY"])

result = dk.nrds.list(query="shop", tld="com")
print(result["total"], "matches")
```

Parameters are passed as keyword arguments using the REST parameter names, verbatim.

## Endpoints

Search resources, each with `list`, `paginate` and `export`:

| Resource | Endpoint |
|---|---|
| `dk.expired` | `/search/expired` |
| `dk.nrds` | `/search/nrds` |
| `dk.nrds_live` | `/search/nrds-live` |
| `dk.aged` | `/search/aged` |
| `dk.active` | `/search/active` |
| `dk.deleted` | `/search/deleted` |
| `dk.market` | `/search/market` |

Lookups and reports:

| Method | Endpoint |
|---|---|
| `dk.whois(domain)` | `/whois` |
| `dk.dns(domain)` | `/dns` |
| `dk.bulk_dns(domains)` | `/bulk/dns` |
| `dk.bulk_whois(domains)` | `/bulk/whois` |
| `dk.ip_lookup(query)` | `/ip-lookup` |
| `dk.registrar(query)` | `/registrar` |
| `dk.status_guide(query)` | `/status-guide` |
| `dk.tld_check(prefix)` | `/tld-check` |
| `dk.typosquat(domain)` | `/typosquat` |
| `dk.ns_reverse(ns)` | `/ns-reverse` |
| `dk.monitor_changes()` | `/monitor/changes` |
| `dk.ct_subdomains(domain)` | `/ct/subdomains` |
| `dk.ct_certs()` | `/ct/certs` |
| `dk.ct_search(keyword)` | `/ct/search` |
| `dk.tld_trends(type)` | `/trends/tlds/*` |
| `dk.keyword_trends(type)` | `/trends/keywords/*` |
| `dk.nrds_download()` | `/nrds/download` |
| `dk.usage()` | `/usage` |
| `dk.search_status()` | `/search/status` |
| `dk.health()` | `/health` |

The [API reference](https://domainkits.com/dev/api-docs) is the authority on every filter, field and limit.

**No PII.** Responses contain no registrant personal data.

## Errors

```python
from domainkits import DomainKits, RateLimitError, AuthError, DomainKitsError

try:
    dk.whois("example.com")
except RateLimitError as err:
    print("retry after", err.retry_after_ms, "ms")
except AuthError as err:
    print("key rejected:", err)
except DomainKitsError as err:
    print(err.status, err)
```

`RateLimitError` (429) carries the rate-limit headers and a `retry_after_ms`; the client retries 429 and 5xx responses on its own up to `max_retries` before raising.

## Options

```python
dk = DomainKits(
    "dk_...",
    base_url="https://premium-api.domainkits.com/api/v1",
    timeout=60.0,
    max_retries=2,
)
```

## Resources

- [API reference and key management](https://domainkits.com/dev)
- [OpenAPI 3.0 spec](https://domainkits.com/dev/openapi.yaml)
- [About DomainKits and ABTdomain](https://domainkits.com/about)

## License

[MIT](LICENSE)

[![PyPI](https://img.shields.io/pypi/v/domainkits?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/domainkits/)
[![Python](https://img.shields.io/pypi/pyversions/domainkits?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/domainkits/)
[![License](https://img.shields.io/pypi/l/domainkits?style=flat-square)](LICENSE)

# domainkits

Python client for the [DomainKits](https://domainkits.com) domain data API. It runs on the standard library, with no other dependencies.

## What it does

It brings domain data into your Python code, so your services, scheduled jobs and pipelines can search it, look it up and download it as part of their own logic:

- **Lifecycle**: [newly registered domains](https://github.com/ABTdomain/newly-registered-domains) as a search or as the daily list, [expired domains](https://github.com/ABTdomain/expired-domains) as a search or as an exported file, and deleted, aged, active and for-sale domains
- **Registration**: WHOIS data, the registrar, and what each EPP status code means
- **DNS and hosting**: DNS records, the network behind an IP, and other domains on the same nameserver
- **Certificates**: subdomains, certificates and newly seen hostnames from CT logs
- **Footprint**: the same name across TLDs, and typosquat variants around a brand
- **Trends**: keyword and TLD registration trends
- **Changes**: transfers, drops, renewals and nameserver updates on high-value domains

▶ [See how it is used](#use-it-for)

## Endpoints

Search resources, each with `list`, `paginate` and `export`:

| Resource | Endpoint |
|---|---|
| `dk.expired` | `/search/expired` |
| `dk.nrds` | `/search/nrds` |
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
| `dk.hostname_search(q)` | `/search/hostname` |
| `dk.ct_subdomains(domain)` | `/ct/subdomains` |
| `dk.ct_certs()` | `/ct/certs` |
| `dk.tld_trends(type)` | `/trends/tlds/*` |
| `dk.keyword_trends(type)` | `/trends/keywords/*` |
| `dk.nrds_download()` | `/nrds/download` |
| `dk.usage()` | `/usage` |
| `dk.search_status()` | `/search/status` |
| `dk.health()` | `/health` |

Filters, fields and limits for each endpoint are in the [API reference](https://domainkits.com/dev/api-docs).

**No PII.** Responses contain no registrant personal data.

## Install

```bash
pip install domainkits
```

Set your key and make a call:

```python
import os
from domainkits import DomainKits

dk = DomainKits(os.environ["DOMAINKITS_API_KEY"])

result = dk.nrds.list(query="shop", tld="com")
print(result["total"], "matches")
```

Parameters are passed as keyword arguments using the REST parameter names, verbatim.

The same key works for the REST API, the SDKs, the MCP server and the CLI.

Sign up at [domainkits.com](https://domainkits.com/register) and create a key on your [dashboard](https://domainkits.com/dashboard). `dk.nrds_download()` works on a free account; the other calls need a plan that includes the API, see the [API reference](https://domainkits.com/dev/api-docs).

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

## Use it for

### [Newly registered domains](https://github.com/ABTdomain/newly-registered-domains)

```python
dk.nrds.list(query="ai", tld="com")                  # search by keyword
dk.nrds_download(tld="com", type="domains_only")     # pull the daily list
```

<p align="center">
<a href="https://www.youtube.com/watch?v=8bXfKV5-eGw"><img src="https://img.youtube.com/vi/8bXfKV5-eGw/maxresdefault.jpg" alt="Video: How to get a newly registered domains feed with the DomainKits API" width="640"></a><br>
<a href="https://www.youtube.com/watch?v=8bXfKV5-eGw">▶ Watch on YouTube: How to Get a Newly Registered Domains Feed with an API</a>
</p>

### [Expired domains](https://github.com/ABTdomain/expired-domains)

```python
dk.expired.list(query="shop", status="pending_delete", age_min=10)   # pending delete names with a long history
dk.expired.export(tld="app", status="redemption")                    # one TLD's redemption stage as CSV
```

## Related

- [ABTdomain/domainkits-sdk-go](https://github.com/ABTdomain/domainkits-sdk-go): Go client for the DomainKits domain data API
- [ABTdomain/domainkits-sdk-js](https://github.com/ABTdomain/domainkits-sdk-js): TypeScript client for the DomainKits domain data API
- [ABTdomain/domainkits-cli](https://github.com/ABTdomain/domainkits-cli): command-line client for the DomainKits domain data API
- [ABTdomain/domainkits-mcp](https://github.com/ABTdomain/domainkits-mcp): hosted MCP server for domain data

## Resources

- [API reference and key management](https://domainkits.com/dev)
- [OpenAPI 3.0 spec](https://domainkits.com/dev/openapi.yaml)
- [About DomainKits and ABTdomain](https://domainkits.com/about)

## License

[MIT](LICENSE)

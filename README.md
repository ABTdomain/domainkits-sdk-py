# domainkits

Python client for the [DomainKits](https://domainkits.com) REST API.

DomainKits is one API with a shared key across every endpoint. This package covers all of them, six domain search types, WHOIS, DNS, reverse nameserver, Certificate Transparency, safety, trends and bulk download, with automatic paging and structured quota errors. No dependencies.

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

result = dk.expired.list(
    keyword="clinic",
    tld="com",
    length="5-10",
    no_number=True,
    no_hyphen=True,
)

print(f"{result['total']} matches")
for d in result["data"]:
    print(d["domain"], d["age"], d["status"])
```

### Paging

A single request returns at most 500 results. `paginate` walks the whole result set for you:

```python
for domain in dk.expired.paginate(keyword="clinic", tld="com"):
    print(domain["domain"])
```

It stops when the result set is exhausted. Break out of the loop whenever you have enough; no further requests are made.

### Export

`export` pulls up to 50,000 rows as CSV in one request:

```python
csv = dk.expired.export(tld="com", status="pending_delete")
```

This runs on a separate, much smaller quota, 10 per day and 100 per month on Premium, 3 and 9 during the trial. It is for occasional bulk pulls, not for a scheduled job. The export also returns fewer columns than paged mode: `registered_date` is the year only, and `age` is omitted.

50,000 is a cap, not a promise of completeness. Browsing `.com` matched 4,847,613 expiring domains on 27 July 2026, so an unfiltered export returns the first 50,000. Narrow the query if you need the result set to fit.

## Search types

| Attribute | What it searches |
|---|---|
| `dk.expired` | Domains in the deletion cycle: expired, redemption, pending delete |
| `dk.nrds` | Newly registered domains, last 60 days |
| `dk.aged` | Domains with 5 to 20+ years of registration history |
| `dk.active` | Currently registered domains |
| `dk.deleted` | Dropped domains (requires `keyword`) |
| `dk.market` | Domains listed for sale on marketplaces |

Each has `list`, `paginate` and `export`. Filters are passed as keyword arguments and match the REST parameter names: an expired result carries `status`, an NRD result carries `expiry_date`, a market result carries `marketplace`.

## Other endpoints

```python
dk.whois("example.com")
dk.dns("example.com")
dk.safety("example.com")
dk.ns_reverse("ns1.example.com", tld="com")
dk.tld_check("yourbrand")
dk.typosquat("example.com")
dk.ip_lookup("8.8.8.8")
dk.registrar("godaddy")
dk.status_guide("clientHold")
dk.monitor_changes(tld="com", reason="transfer")
dk.ct_subdomains("example.com")
dk.ct_certs(domain="example.com")
dk.ct_search("example")
dk.tld_trends("newly", tld="com")
dk.keyword_trends("hot")
dk.usage()
dk.search_status()
```

## Coverage

**gTLDs only** for the domain search endpoints. The index covers generic TLDs: `.com`, `.net`, `.org`, `.info`, `.biz`, `.xyz`, `.online`, `.site`, `.top`, `.club`, `.live`, `.app`, `.dev` and others. Country-code TLDs are not indexed: a query for `.de`, `.io`, `.co` or `.us` returns an empty result set, not an error.

`whois`, `dns`, `safety`, `ip_lookup` and the Certificate Transparency endpoints work on any domain, ccTLDs included.

**No PII.** Responses contain no personal data. WHOIS results are limited to registrar, dates, status codes and nameservers; registrant names, emails, addresses and phone numbers are not returned.

## Errors

```python
from domainkits import DomainKits, DomainKitsError, RateLimitError, AuthError

try:
    dk.expired.export(tld="com")
except RateLimitError as error:
    print(f"Quota exhausted. Retry in {error.retry_after_ms}ms")
    print(error.rate_limit)
except AuthError:
    print("Key rejected, check your plan tier")
except DomainKitsError as error:
    print(error.status, error)
```

Every error carries the `x-ratelimit-limit`, `x-ratelimit-remaining` and `x-ratelimit-reset` values as a parsed `rate_limit` object. `RateLimitError.retry_after_ms` tells you how long until the window resets.

429 and 5xx responses are retried automatically, twice by default, waiting until the rate-limit window resets when that is under two minutes. Set `max_retries=0` to handle it yourself.

## Options

```python
dk = DomainKits(
    api_key=os.environ["DOMAINKITS_API_KEY"],
    timeout=60.0,
    max_retries=2,
    base_url="https://premium-api.domainkits.com/api/v1",
)
```

## Quotas

Call `usage()` for the live picture on your account; every endpoint reports its own per-minute, daily and monthly allowance alongside what you have already spent.

Daily quotas reset at 00:00 UTC, monthly quotas on the 1st. Current limits: [domainkits.com/dev/api-docs](https://domainkits.com/dev/api-docs).

## Resources

- [DomainKits API reference](https://domainkits.com/dev/api-docs)
- [@domainkits/sdk](https://www.npmjs.com/package/@domainkits/sdk), the same API for TypeScript
- [n8n-nodes-domainkits](https://www.npmjs.com/package/n8n-nodes-domainkits), the same API for n8n

## License

MIT

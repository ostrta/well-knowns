# well-knowns.com — OpenClaw Agent Business Plan
**Operator:** Matt | **Domain:** well-knowns.com | **Platform:** resolved.sh | **Revenue:** USDC via x402

---

## Executive Summary

This plan instructs OpenClaw to build and operate a self-sustaining data business on resolved.sh using the domain **well-knowns.com**. The business crawls the internet's publicly declared `/.well-known/` endpoints — standardized URLs where servers publish structured metadata about themselves — and sells the resulting dataset as a regularly refreshed, agent-consumable product.

The timing is intentional. Two IANA-registered well-known types — `agent-card.json` (Google's A2A agent discovery standard, registered August 2025, 150+ enterprise backers) and `oauth-protected-resource` (required by the MCP auth spec) — have no comprehensive public catalog. The buyers for this data are other autonomous agents that need to discover services, authenticate to APIs, and find AI agents to delegate work to. The entire transaction loop is agent-to-agent, paid in USDC, with no human required on either side.

**The business in one sentence:** Compile and sell the definitive index of how the internet describes itself to machines, starting with the top 100k most-visited domains.

---

## 1. Competitive Landscape — Read This First

Before building, understand what already exists. This context should shape every product and prioritization decision.

### SSO-Monitor (sso-monitor.me)

An academic project from Ruhr University Bochum that crawls the Tranco top 1M domains for SSO-related well-known endpoints including `openid-configuration` and `oauth-authorization-server`. It is:
- **Free** — no charge for access
- **Open source** — fully transparent methodology
- **Research-grade** — reliability and SLA not guaranteed
- **Narrowly scoped** — focused on SSO landscape measurement, not agent infrastructure
- **Not agent-consumable** — data is not packaged for autonomous agent querying or x402 purchase

**Implication:** Do not position the product as "OIDC endpoint discovery." Position it as "the agent infrastructure index." The two agent-ecosystem well-known types — `agent-card.json` and `mcp.json` — are wide open. SSO-Monitor does not cover them. This is the moat.

### Common Crawl / Shodan

Large-scale internet scan projects exist but are not maintained as normalized, typed, agent-queryable datasets for well-known endpoint types. They are raw and not structured for the use case.

### The Gap

No commercial product exists that provides a daily-refreshed, normalized, agent-consumable catalog of the emerging agent discovery infrastructure: `agent-card.json`, `mcp.json`, `oauth-protected-resource`. This is the window to occupy.

---

## 2. Well-Known Types to Crawl

The IANA Well-Known URI Registry (iana.org/assignments/well-known-uris) lists approximately 130 registered types. Do not crawl all of them. Crawl the 7 types below, ranked by strategic importance. Add types as the ecosystem evolves.

### Priority 1 — Agent Ecosystem (the moat)

**`/.well-known/agent-card.json`**
- What it is: Google's A2A (Agent2Agent) protocol discovery document. Published by any agent that supports A2A interoperability. Contains the agent's name, capabilities (skills), endpoint URL, supported authentication flows, and version.
- IANA status: Permanent registration, August 2025
- Current prevalence: Very low (estimated <500 live globally today), growing rapidly. 150+ enterprise organizations backing A2A as of February 2026.
- Why buyers want it: An agent that wants to delegate a task needs to discover available agents. This is the phone book. Nobody is building it yet.
- Parse target: `name`, `description`, `url`, `version`, `capabilities`, `defaultInputModes`, `defaultOutputModes`, `skills[]`

**`/.well-known/oauth-protected-resource`**
- What it is: RFC 9728 (2025). Published by any OAuth-protected resource server (including MCP servers) to declare which authorization server to trust, what scopes exist, and how to obtain tokens.
- IANA status: Permanent registration
- Current prevalence: Low overall, but every spec-compliant MCP server is required to publish this. Growing directly with MCP adoption.
- Why buyers want it: An agent connecting to an MCP server needs to know where to get auth tokens before it can authenticate. This is required pre-flight data.
- Parse target: `resource`, `authorization_servers[]`, `scopes_supported[]`, `bearer_methods_supported[]`

**`/.well-known/mcp.json`**
- What it is: MCP server capability discovery. Allows a client to discover an MCP server's tools, capabilities, and connection details without establishing a full MCP session. Shopify is deploying this across millions of storefronts.
- IANA status: Proposal active as of February 2026 (PR #2127 in MCP spec repo)
- Current prevalence: Very low but imminent spike (Shopify + major platform deployments expected)
- Why buyers want it: Agents building MCP client connections need to know what a server offers before connecting. Discovery without connection.
- Parse target: `name`, `version`, `tools[]`, `capabilities`, `endpoint`

### Priority 2 — Auth Infrastructure (established, high value)

**`/.well-known/openid-configuration`**
- What it is: OpenID Connect Discovery. The standard document published by every OIDC identity provider describing its endpoints, supported flows, and cryptographic keys.
- IANA status: Permanent
- Current prevalence: ~3-8% of top 100k domains (~3,000-8,000 records expected). Every major platform (Google, Microsoft, GitHub, Okta, Auth0, Cognito, etc.) publishes this.
- Why buyers want it: An agent that needs to authenticate with a third-party service must find the authorization endpoint, token endpoint, and JWKS URI before it can proceed. This is the most mature and widely deployed well-known type relevant to agent auth.
- Parse target: `issuer`, `authorization_endpoint`, `token_endpoint`, `jwks_uri`, `scopes_supported[]`, `grant_types_supported[]`, `response_types_supported[]`
- Competition note: SSO-Monitor covers this. Differentiate on freshness, normalization quality, and bundling with Priority 1 types.

**`/.well-known/oauth-authorization-server`**
- What it is: RFC 8414. The OAuth 2.0 Authorization Server Metadata document. Closely related to OIDC discovery but for OAuth 2.0 servers that do not implement OpenID Connect.
- IANA status: Permanent
- Current prevalence: ~2-5% of top 100k. Significant overlap with `openid-configuration` deployments.
- Parse target: `issuer`, `authorization_endpoint`, `token_endpoint`, `scopes_supported[]`, `grant_types_supported[]`

### Priority 3 — Signal and Coverage

**`/.well-known/security.txt`**
- What it is: RFC 9116. A structured plain-text file with security contact information, disclosure policies, and PGP keys.
- IANA status: Permanent
- Current prevalence: ~5-15% of top 100k (~5,000-15,000 records). The most widely deployed well-known type.
- Why buyers want it: Agents performing security assessments or responsible disclosure automation need this. Good volume filler for dataset richness.
- Parse target: `Contact:`, `Expires:`, `Encryption:`, `Policy:`, `Acknowledgments:`

**`/.well-known/host-meta`**
- What it is: RFC 6415. A metadata document describing available resources and protocols for a host. Used as a base for WebFinger and federation protocols.
- Parse target: Link relations, href values
- Note: Lower priority. Include if crawl overhead is low.

---

## 3. Data Sources — Tier 1 (GTM)

### Primary: Tranco Top 100k

Tranco (tranco-list.eu) is the authoritative academic domain ranking list. It aggregates five source lists — Cisco Umbrella (DNS traffic), Majestic (backlink graph), Farsight (passive DNS), Chrome User Experience Report (CrUX), and Cloudflare Radar — using the Dowdall rule over a 30-day rolling window. The result is more stable and manipulation-resistant than any single source.

**Why top 100k, not top 1M for GTM:**
The top 100k domains have the highest density of professionally maintained servers with actual well-known infrastructure. Crawling 1M domains at launch means 85%+ of crawl effort hits domains with zero relevant endpoints. Start at 100k, expand after the pipeline is proven.

**Fetching the list:**

```python
pip install tranco
```

```python
from tranco import Tranco
t = Tranco(cache=True, cache_dir=".tranco")
latest = t.list()
top_100k = latest.top(100000)  # Returns list of domain strings
# top_100k[0] = 'google.com', top_100k[1] = 'youtube.com', etc.
```

Alternatively, fetch directly:
```bash
curl -o tranco-top1m.csv.zip https://tranco-list.eu/top-1m.csv.zip
unzip tranco-top1m.csv.zip
head -100000 top-1m.csv | cut -d',' -f2 > domains-100k.txt
```

**Update cadence:** Tranco updates daily at 00:00 UTC. Refresh the domain list weekly — daily Tranco changes are minor, and re-crawling stable domains wastes resources. On weekly refresh, only crawl domains that are new to the list or that haven't been crawled in 7 days.

**Secondary source (optional enrichment):** Cloudflare Radar API provides an independent top-domain feed. Use it as a deduplication check or to catch domains the Tranco composite misses. Free API token available at dash.cloudflare.com.

---

## 4. Crawling Architecture

### Tech Stack

- **Language:** Python 3.11+
- **HTTP:** `httpx` with async support (preferred over aiohttp for cleaner API; supports HTTP/2)
- **Concurrency:** `asyncio` with semaphore-limited concurrent requests
- **Storage:** JSONL (JSON Lines) for raw data; filtered JSON files for product artifacts
- **Scheduling:** System cron or resolved.sh's native scheduling primitives

### Concurrency Model

100k domains × 7 endpoints = 700,000 HTTP requests per full crawl.

At 50 concurrent requests with a 5-second timeout:
- Estimated crawl time: ~2-4 hours (varies heavily on response rates)
- Safe rate that avoids mass blocking: 50 concurrent, 1-second delay between domain batches

```python
import asyncio
import httpx
import json
from datetime import datetime, timezone

WELL_KNOWN_PATHS = [
    "agent-card.json",
    "oauth-protected-resource",
    "mcp.json",
    "openid-configuration",
    "oauth-authorization-server",
    "security.txt",
]

SEMAPHORE_LIMIT = 50
REQUEST_TIMEOUT = 5.0
MAX_REDIRECTS = 3

async def probe_domain(client: httpx.AsyncClient, domain: str) -> dict:
    result = {
        "domain": domain,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "endpoints": {}
    }
    for path in WELL_KNOWN_PATHS:
        url = f"https://{domain}/.well-known/{path}"
        try:
            r = await client.get(url, follow_redirects=True)
            endpoint_result = {
                "status": r.status_code,
                "response_time_ms": int(r.elapsed.total_seconds() * 1000),
                "content_type": r.headers.get("content-type", ""),
                "data": None,
                "raw": None,
                "error": None
            }
            if r.status_code == 200:
                ct = r.headers.get("content-type", "")
                if "json" in ct:
                    try:
                        endpoint_result["data"] = r.json()
                    except Exception:
                        endpoint_result["raw"] = r.text[:4096]
                        endpoint_result["error"] = "json_parse_failed"
                else:
                    endpoint_result["raw"] = r.text[:4096]
        except httpx.TimeoutException:
            endpoint_result = {"status": None, "error": "timeout"}
        except httpx.ConnectError:
            endpoint_result = {"status": None, "error": "connect_error"}
        except Exception as e:
            endpoint_result = {"status": None, "error": str(e)[:128]}

        result["endpoints"][path] = endpoint_result
    return result

async def crawl_batch(domains: list[str], output_path: str):
    sem = asyncio.Semaphore(SEMAPHORE_LIMIT)
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=50)

    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
        max_redirects=MAX_REDIRECTS,
        limits=limits,
        headers={"User-Agent": "well-knowns-bot/1.0 (+https://well-knowns.com/bot)"}
    ) as client:
        async def bounded_probe(domain):
            async with sem:
                return await probe_domain(client, domain)

        tasks = [bounded_probe(d) for d in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    with open(output_path, "a") as f:
        for r in results:
            if isinstance(r, dict):
                f.write(json.dumps(r) + "\n")

async def main(domain_file: str, output_path: str):
    with open(domain_file) as f:
        domains = [line.strip() for line in f if line.strip()]

    # Process in batches of 1000 to allow checkpointing
    batch_size = 1000
    for i in range(0, len(domains), batch_size):
        batch = domains[i:i + batch_size]
        await crawl_batch(batch, output_path)
        print(f"Completed batch {i//batch_size + 1}/{len(domains)//batch_size + 1}")
        await asyncio.sleep(1)  # Brief pause between batches

if __name__ == "__main__":
    asyncio.run(main("domains-100k.txt", "raw-crawl.jsonl"))
```

### Rate Limiting and Politeness

- Respect `429 Too Many Requests` responses — back off exponentially and retry after the `Retry-After` header value
- Do not retry 403 or 404 — these are definitive
- Retry 5xx errors once after 30 seconds
- The `User-Agent` string above identifies the bot with a contact URL — this is best practice and reduces blocks
- Spread crawls across the day rather than hammering all 100k at once on a tight schedule

### Error Handling

Track and log:
- Domains that consistently time out (may be unreachable — mark as `unreachable` after 3 consecutive failures)
- Domains that return unexpected content-types for JSON endpoints (indicates misconfiguration, still worth storing)
- Redirect chains longer than 3 hops (skip and flag)
- SSL certificate errors (log separately — useful signal)

---

## 5. Data Schema

### Raw Record (JSONL, one line per domain)

```json
{
  "domain": "example.com",
  "crawled_at": "2026-03-23T14:32:11Z",
  "tranco_rank": 1847,
  "endpoints": {
    "agent-card.json": {
      "status": 200,
      "response_time_ms": 143,
      "content_type": "application/json",
      "data": {
        "name": "Example Agent",
        "description": "...",
        "url": "https://example.com/agent",
        "version": "1.0",
        "capabilities": {},
        "skills": []
      },
      "error": null
    },
    "openid-configuration": {
      "status": 200,
      "response_time_ms": 89,
      "content_type": "application/json",
      "data": {
        "issuer": "https://example.com",
        "authorization_endpoint": "https://example.com/oauth/authorize",
        "token_endpoint": "https://example.com/oauth/token",
        "jwks_uri": "https://example.com/.well-known/jwks.json",
        "scopes_supported": ["openid", "profile", "email"]
      },
      "error": null
    },
    "oauth-protected-resource": {
      "status": 404,
      "error": "not_found"
    },
    "mcp.json": {
      "status": 404,
      "error": "not_found"
    },
    "oauth-authorization-server": {
      "status": 404,
      "error": "not_found"
    },
    "security.txt": {
      "status": 200,
      "response_time_ms": 67,
      "content_type": "text/plain",
      "data": null,
      "raw": "Contact: security@example.com\nExpires: 2027-01-01T00:00:00Z\n",
      "error": null
    }
  }
}
```

### Validation Rules (apply before publishing any record)

```python
def is_valid_record(record: dict) -> bool:
    # Must have a domain
    if not record.get("domain"):
        return False
    # Domain must look like a real domain (not IP, not localhost)
    domain = record["domain"]
    if domain.startswith("192.") or domain == "localhost":
        return False
    # At least one endpoint must have been attempted
    if not record.get("endpoints"):
        return False
    # For JSON endpoints, validate that 200 responses actually contain JSON
    for path, ep in record["endpoints"].items():
        if ep.get("status") == 200 and path.endswith(".json"):
            if ep.get("data") is None and ep.get("error") is None:
                return False  # 200 with no data and no error is suspicious
    return True
```

---

## 6. Products to Sell

Five distinct datasets, each optimized for a specific buyer type. All sold via resolved.sh x402 micropayment on download.

### Product 1 — Full Catalog (Weekly Snapshot)
**Filename pattern:** `full-catalog-YYYY-MM-DD.jsonl`
**Price:** $3.00 USDC per download
**Contents:** All 100k domains, all 7 endpoint types, raw validated records. Full JSONL, approximately 200-500 MB uncompressed.
**Buyer:** Agents that want to build their own filtering, analysis, or downstream products. Infrastructure-layer buyers.
**Refresh:** Weekly (full re-crawl every 7 days)
**Update signal:** Include a lightweight `catalog-manifest.json` (free, $0.00) that lists available snapshots, their dates, record counts, and hit rates by endpoint type. Buyers check this before deciding to download the full file.

### Product 2 — OIDC Provider Directory
**Filename pattern:** `oidc-providers-YYYY-MM-DD.json`
**Price:** $1.50 USDC per download
**Contents:** Filtered extract. Only domains with a valid (200 OK, parseable JSON) `openid-configuration` response. Includes parsed and normalized fields: `issuer`, `authorization_endpoint`, `token_endpoint`, `jwks_uri`, `scopes_supported`. Expected record count: 3,000–8,000.
**Buyer:** Agents that need to authenticate with arbitrary OAuth-enabled services. The classic use case: "I need to get a token from this provider — where do I send the auth request?"
**Refresh:** Weekly, tied to the Full Catalog crawl
**Format:** Array of objects (not JSONL) for easy in-memory consumption

```json
[
  {
    "domain": "github.com",
    "tranco_rank": 4,
    "crawled_at": "2026-03-23T14:00:00Z",
    "issuer": "https://token.actions.githubusercontent.com",
    "authorization_endpoint": "https://github.com/login/oauth/authorize",
    "token_endpoint": "https://github.com/login/oauth/access_token",
    "jwks_uri": "https://token.actions.githubusercontent.com/.well-known/jwks",
    "scopes_supported": ["openid", "repo", "user", "gist"]
  }
]
```

### Product 3 — Agent Discovery Index
**Filename pattern:** `agent-index-YYYY-MM-DD.json`
**Price:** $1.00 USDC per download (intentionally cheap — drive adoption now, raise price as ecosystem matures)
**Contents:** All domains with a valid `agent-card.json` response. Includes parsed agent name, description, endpoint URL, skills, and supported auth flows.
**Buyer:** Orchestrator agents looking to delegate tasks to specialized agents. This is the core use case of A2A — find an agent that can do what you need. Expected record count today: very small (<100). Expected in 12 months: thousands.
**Refresh:** Daily (this dataset is growing fast; daily freshness matters more than for OIDC)
**Strategic note:** This product has low revenue today but establishes well-knowns.com as the canonical A2A agent registry before anyone else does. It is the long-term moat. Prioritize it.

### Product 4 — MCP Infrastructure Map
**Filename pattern:** `mcp-infrastructure-YYYY-MM-DD.json`
**Price:** $1.00 USDC per download
**Contents:** Domains with either a valid `mcp.json` or `oauth-protected-resource` response (or both). Parsed to show MCP server endpoint, tools list (if available), and the authorization server URL from `oauth-protected-resource`.
**Buyer:** Agents building MCP client connections that need pre-flight discovery — "does this domain run an MCP server and how do I auth to it?"
**Refresh:** Daily

```json
[
  {
    "domain": "shopify.com",
    "tranco_rank": 52,
    "crawled_at": "2026-03-23T14:00:00Z",
    "mcp_json": {
      "name": "Shopify MCP Server",
      "version": "1.0",
      "endpoint": "https://shopify.com/mcp",
      "tools": ["search_products", "get_order", "create_cart"]
    },
    "oauth_protected_resource": {
      "resource": "https://shopify.com/mcp",
      "authorization_servers": ["https://accounts.shopify.com"],
      "scopes_supported": ["read_products", "write_orders"]
    }
  }
]
```

### Product 5 — Delta Update (Daily Changes)
**Filename pattern:** `delta-YYYY-MM-DD.jsonl`
**Price:** $0.50 USDC per download
**Contents:** Only domains where any endpoint changed since the previous crawl. A domain appears in the delta if: a previously-404 endpoint now returns 200 (new deployment), a previously-200 endpoint now returns 404 (takedown), or parsed JSON content changed materially.
**Buyer:** Agents that already have the Full Catalog and need to stay current without re-downloading 500MB weekly. Ideal for caching agents.
**Refresh:** Daily
**Implementation:** Diff each domain's current record against the previous crawl snapshot. Track changes with `change_type: "appeared" | "disappeared" | "modified"`.

---

## 7. resolved.sh Integration

### Listing Structure

Create one listing per product. Each listing represents a recurring data feed. The listing description should communicate clearly to agent buyers what the data contains, how fresh it is, and what format it is in.

Refer to resolved.sh API documentation for the exact listing creation and data upload endpoints. Based on the documented pattern, the data upload call follows:

```
PUT /listing/{listing_id}/data/{filename}?price_usdc={price}
Content-Type: application/octet-stream
[file body]
```

### Recommended Listing Metadata

**Listing: Full Catalog**
```
name: well-knowns.com Full Catalog
description: Weekly snapshot of /.well-known/ endpoint probes across the Tranco top 100k
domains. Covers 7 endpoint types: agent-card.json, oauth-protected-resource, mcp.json,
openid-configuration, oauth-authorization-server, oauth-authorization-server, security.txt.
JSONL format, one record per domain. Validated and normalized. Updated every Monday.
price_usdc: 3.00
```

**Listing: OIDC Provider Directory**
```
name: well-knowns.com OIDC Provider Directory
description: Filtered extract of all domains in the top 100k with a live
/.well-known/openid-configuration endpoint. Normalized JSON array with parsed issuer,
authorization_endpoint, token_endpoint, jwks_uri, and scopes_supported. Ready to
query directly. Updated weekly.
price_usdc: 1.50
```

**Listing: Agent Discovery Index**
```
name: well-knowns.com Agent Discovery Index (A2A)
description: All domains in the top 100k with a live /.well-known/agent-card.json
(Google A2A protocol). Parsed agent name, skills, endpoint, and auth flows. The
canonical index of publicly discoverable AI agents. Updated daily.
price_usdc: 1.00
```

**Listing: MCP Infrastructure Map**
```
name: well-knowns.com MCP Infrastructure Map
description: All domains with live /.well-known/mcp.json or
/.well-known/oauth-protected-resource endpoints. Includes MCP server capabilities and
authorization server URLs for pre-flight MCP auth discovery. Updated daily.
price_usdc: 1.00
```

**Listing: Delta Updates**
```
name: well-knowns.com Daily Delta
description: Daily diff against the previous crawl. Contains only domains where
endpoint status or content changed. Fields: domain, change_type (appeared/disappeared/
modified), endpoint, previous_status, current_status. Ideal for cache invalidation.
Updated daily at 06:00 UTC.
price_usdc: 0.50
```

### Free Catalog Manifest (Important)

Create one additional listing priced at $0.00 for the catalog manifest:

```json
{
  "last_updated": "2026-03-23T06:00:00Z",
  "crawl_date": "2026-03-22",
  "domains_crawled": 100000,
  "hit_rates": {
    "agent-card.json": 0.0008,
    "oauth-protected-resource": 0.0031,
    "mcp.json": 0.0012,
    "openid-configuration": 0.0621,
    "oauth-authorization-server": 0.0394,
    "security.txt": 0.1047
  },
  "products": [
    {
      "name": "Full Catalog",
      "filename": "full-catalog-2026-03-22.jsonl",
      "record_count": 100000,
      "file_size_bytes": 312490882,
      "price_usdc": 3.00
    }
  ]
}
```

This manifest serves as a discovery document for buyer agents evaluating whether to purchase. A buyer agent can fetch it for free, see the hit rates and record counts, and decide which product to buy. Free signals increase conversion on paid products.

---

## 8. Operational Schedule

### Daily Pipeline (run every day at 02:00 UTC)

```
1. Fetch Tranco list (cache; only re-fetch if >7 days old)
2. Load domain list
3. Run async crawler — Priority 1 + Priority 2 endpoints only
   - For domains not yet in this week's full crawl: full 7-endpoint probe
   - For domains already probed this week: probe Priority 1 only (agent-card, mcp, oauth-protected-resource)
4. Validate and write records
5. Generate Product 3 (Agent Discovery Index) — filter, format, upload
6. Generate Product 4 (MCP Infrastructure Map) — filter, format, upload
7. Generate Product 5 (Delta) — diff against previous day's snapshot
8. Update catalog manifest — upload at $0.00
```

### Weekly Pipeline (run every Monday at 04:00 UTC)

```
1. Fetch fresh Tranco top 100k (check for new domains vs. last week)
2. Run full crawl — all 7 endpoint types across all 100k domains
3. Generate Product 1 (Full Catalog) — upload at $3.00
4. Generate Product 2 (OIDC Provider Directory) — upload at $1.50
5. Archive previous week's files (keep 4 weeks of history)
6. Update catalog manifest
7. Log crawl statistics (domains probed, hit rates by type, errors, response time p50/p95)
```

### Checkpoint and Recovery

- Write crawl progress to a local state file (`crawl-state.json`) after every 1,000 domains
- On restart after failure, skip already-crawled domains in the current run
- If a crawl run fails to complete within 6 hours, alert and abort — do not publish a partial dataset

---

## 9. Processing Pipeline Detail

### After Raw Crawl

```python
import json
from pathlib import Path

def generate_oidc_directory(raw_jsonl_path: str) -> list:
    """Filter and normalize OIDC providers from raw crawl data."""
    results = []
    with open(raw_jsonl_path) as f:
        for line in f:
            record = json.loads(line)
            ep = record["endpoints"].get("openid-configuration", {})
            if ep.get("status") != 200 or not ep.get("data"):
                continue
            data = ep["data"]
            if not data.get("issuer") or not data.get("token_endpoint"):
                continue  # Malformed OIDC config — skip
            results.append({
                "domain": record["domain"],
                "tranco_rank": record.get("tranco_rank"),
                "crawled_at": record["crawled_at"],
                "issuer": data.get("issuer"),
                "authorization_endpoint": data.get("authorization_endpoint"),
                "token_endpoint": data.get("token_endpoint"),
                "jwks_uri": data.get("jwks_uri"),
                "userinfo_endpoint": data.get("userinfo_endpoint"),
                "scopes_supported": data.get("scopes_supported", []),
                "grant_types_supported": data.get("grant_types_supported", []),
                "response_types_supported": data.get("response_types_supported", []),
            })
    return sorted(results, key=lambda x: x.get("tranco_rank") or 999999)

def generate_agent_index(raw_jsonl_path: str) -> list:
    """Filter agent-card.json hits."""
    results = []
    with open(raw_jsonl_path) as f:
        for line in f:
            record = json.loads(line)
            ep = record["endpoints"].get("agent-card.json", {})
            if ep.get("status") != 200 or not ep.get("data"):
                continue
            data = ep["data"]
            results.append({
                "domain": record["domain"],
                "tranco_rank": record.get("tranco_rank"),
                "crawled_at": record["crawled_at"],
                "name": data.get("name"),
                "description": data.get("description"),
                "url": data.get("url"),
                "version": data.get("version"),
                "skills": data.get("skills", []),
                "capabilities": data.get("capabilities", {}),
                "default_input_modes": data.get("defaultInputModes", []),
                "default_output_modes": data.get("defaultOutputModes", []),
            })
    return results

def generate_delta(prev_jsonl: str, curr_jsonl: str) -> list:
    """Compute changes between two crawl runs."""
    def load_indexed(path):
        records = {}
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                records[r["domain"]] = r
        return records

    prev = load_indexed(prev_jsonl)
    curr = load_indexed(curr_jsonl)

    deltas = []
    priority_endpoints = ["agent-card.json", "mcp.json", "oauth-protected-resource",
                          "openid-configuration", "oauth-authorization-server"]

    for domain, curr_rec in curr.items():
        prev_rec = prev.get(domain, {})
        for ep_name in priority_endpoints:
            curr_ep = curr_rec.get("endpoints", {}).get(ep_name, {})
            prev_ep = prev_rec.get("endpoints", {}).get(ep_name, {})
            curr_status = curr_ep.get("status")
            prev_status = prev_ep.get("status")
            if curr_status == prev_status:
                continue
            change_type = (
                "appeared" if curr_status == 200 and prev_status != 200
                else "disappeared" if curr_status != 200 and prev_status == 200
                else "status_change"
            )
            deltas.append({
                "domain": domain,
                "endpoint": ep_name,
                "change_type": change_type,
                "previous_status": prev_status,
                "current_status": curr_status,
                "tranco_rank": curr_rec.get("tranco_rank"),
            })
    return deltas
```

---

## 10. Phase Roadmap

### Phase 1 — Bootstrap (Days 1–7)

**Goal:** Ship a working crawl pipeline and first dataset upload to resolved.sh.

1. Install dependencies: `pip install httpx tranco`
2. Fetch Tranco top 1,000 domains (not 100k — validate the pipeline first)
3. Run crawler against 1k domains, inspect raw JSONL output
4. Verify JSON parsing works correctly for each endpoint type
5. Run generate functions — confirm OIDC directory and agent index produce valid output
6. Create resolved.sh listings for all 5 products
7. Upload first dataset artifacts (even if small — 1k domain run)
8. Upload catalog manifest at $0.00
9. Confirm the x402 purchase flow works end to end

**Success signal:** At least one paid download from a buyer agent.

### Phase 2 — Production Scale (Days 8–21)

**Goal:** Full 100k crawl running on schedule, all products published weekly/daily.

1. Scale crawler to 10k domains — validate performance and error rates
2. Scale to 100k — tune semaphore limits and batch sizes based on observed rates
3. Implement delta generation and daily pipeline
4. Implement checkpoint/recovery logic
5. Monitor hit rates — validate estimates match reality
6. Sweep USDC earnings to wallet daily

**Success signal:** Weekly full crawl completes reliably in under 6 hours, all 5 products published on schedule.

### Phase 3 — Product Refinement (Days 22–45)

**Goal:** Improve data quality, respond to what buyers actually want.

1. Track which products get the most downloads — double down on those
2. Add normalized field extraction for all Priority 1 endpoint types
3. Implement SSL certificate error tracking as a separate signal
4. Begin tracking A2A adoption rate week-over-week (the key growth metric)
5. Consider adding `host-meta` and `webfinger` if demand signals warrant
6. If agent-card.json hit rates grow meaningfully, raise Product 3 price to $2.00

### Phase 4 — Expand to Tier 2 (Day 46+)

**Goal:** Add domain sources beyond Tranco to capture the long tail of agent infrastructure.

1. GitHub API: search repos tagged `mcp-server`, `a2a-agent`, `openid-provider` — extract homepage URLs
2. npm registry: packages tagged `mcp-server` — extract homepage and repository URLs
3. A2A partner registry: as Google's A2A ecosystem matures, official partner lists will emerge — harvest domains from those
4. Crawl the new domains for all 7 endpoint types
5. Publish an "Extended Catalog" product covering the enriched domain set at a higher price point

---

## 11. Success Metrics

### Revenue
- **Week 1 target:** First paid download (validation of purchase flow)
- **Month 1 target:** 10+ downloads/week across all products
- **Month 3 target:** $500+ USDC/month
- **Month 6 target:** $2,000+ USDC/month (scales with A2A ecosystem adoption)

### Data Quality
- Full Catalog completeness: >95% of domains attempted in each crawl
- JSONL validation pass rate: >98% of records pass validation
- OIDC directory accuracy: Spot-check 20 random OIDC records per week — all should return valid token_endpoint
- Agent index freshness: agent-card.json records updated daily

### Ecosystem Signal (lead indicators)
- Week-over-week growth in `agent-card.json` hit count (the A2A adoption curve)
- Week-over-week growth in `mcp.json` hit count (the MCP deployment curve)
- Week-over-week growth in `oauth-protected-resource` hit count (the MCP auth adoption curve)
- These metrics, logged weekly, are the early signal of whether the long-term thesis is playing out

### Operational Health
- Crawl completion time: <6 hours for full 100k run
- Error rate: <5% of domains should return errors (vs. 404/200)
- Crawl failure rate: <1% of runs should require manual intervention

---

## 12. Key Decisions and Rationale

### Why JSONL for the Full Catalog?
JSONL allows streaming — a buyer agent can start processing records without loading 500MB into memory. It also appends cleanly during crawl, allowing incremental writes and easy checkpointing.

### Why $3.00 for the Full Catalog?
The Full Catalog is the upstream product that all filtered products derive from. It is the highest-effort artifact and appropriate for buyers who want to build on top of the data. $3.00 is cheap enough that a well-resourced agent will buy it without friction but meaningful enough to cover compute cost and generate margin.

### Why price the Agent Index at only $1.00?
Low price drives maximum downloads in a market that is just forming. Every agent that buys and uses the index becomes a return customer as the index grows. The index becomes more valuable as A2A adoption grows — price can rise with it. Cheap now is a deliberate growth tactic, not a concession on value.

### Why build the delta product?
Agents are stateful. An agent that already holds the Full Catalog from last week only needs to know what changed. The delta is a $0.50 product that creates a recurring daily revenue stream from buyers who would otherwise only purchase the Full Catalog once a month. It also positions the business as an ongoing data feed, not a one-shot download.

### Why identify the bot honestly in the User-Agent?
Because a bot that hides its identity gets blocked more aggressively and creates legal exposure. A clearly identified, well-behaved crawler that crawls only publicly declared metadata (which `.well-known` is specifically designed for) is on solid technical and ethical ground.

---

## Appendix A — IANA Well-Known URI Registry

The authoritative source for all registered well-known types:
- XML: https://www.iana.org/assignments/well-known-uris/well-known-uris.xml
- Text: https://www.iana.org/assignments/well-known-uris/well-known-uris.txt

Check this registry quarterly for newly registered types relevant to the agent ecosystem.

## Appendix B — Key Reference URLs

- Tranco list download: https://tranco-list.eu/top-1m.csv.zip
- Tranco API: https://tranco-list.eu/api/ranks/domain/{domain}
- Tranco Python package: https://pypi.org/project/tranco/
- SSO-Monitor (competitive reference): https://sso-monitor.me/
- A2A Protocol spec: https://github.com/a2aproject/A2A
- A2A Agent Card schema: https://a2a-protocol.org/latest/topics/agent-discovery/
- MCP Well-Known discussion: https://github.com/modelcontextprotocol/modelcontextprotocol/discussions/1147
- RFC 9728 (oauth-protected-resource): https://www.rfc-editor.org/rfc/rfc9728
- RFC 8414 (oauth-authorization-server): https://www.rfc-editor.org/rfc/rfc8414
- OpenID Connect Discovery spec: https://openid.net/specs/openid-connect-discovery-1_0.html

---

*Plan prepared: March 2026 | For: OpenClaw autonomous agent | Business: well-knowns.com on resolved.sh*

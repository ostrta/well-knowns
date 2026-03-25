# well-knowns.com — Project Roadmap

**Owner:** MClaw (autonomous agent for HClaw)  
**Domain:** well-knowns.com (resolved.sh listing: `ef9f56ad-11a4-43e7-9171-fd108d194ad8`)  
**Inbox:** jollylight927@agentmail.to  
**API Key:** `aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc`  
**Data dir:** `/Users/mclaw/Documents/mclaw/well_knowns/`  
**Raw data dir:** `/Users/mclaw/Documents/mclaw/data/`

---

## Context

well-knowns.com sells regularly-refreshed datasets of `/.well-known/` endpoint probes across the internet's most-visited domains. The target buyer is autonomous agents that need to discover services, authenticate to APIs, and find other agents to delegate to — but the data is also valuable to security researchers and OAuth/OIDC developers.

The business runs on resolved.sh (x402/USDC payments). HClaw owns the domain and listing; MClaw operates the pipeline autonomously.

---

## Architecture

```
Tranco List (top 100k)
       ↓
fetch_domains.py   — download/refresh domain list
       ↓
crawl.py           — async probe of 7 well-known endpoints per domain
       ↓  (raw JSONL, one record per domain)
generate.py        — filter & normalize into 4 derived products
       ↓
upload.py --replace  — push products to resolved.sh listing
       ↓
well-knowns.com (x402 purchase → USDC to HClaw wallet)
```

**Scripts** (`/Users/mclaw/Documents/mclaw/well_knowns/`):
- `fetch_domains.py` — downloads Tranco top N domain list
- `crawl.py` — async crawl, outputs `raw-crawl.jsonl`
- `generate.py` — produces derived products from raw JSONL
- `upload.py` — pushes products to resolved.sh (`--replace` flag required to overwrite)
- `pipeline.py` — orchestrates full phases: bootstrap / full / daily / upload

**Data** (`/Users/mclaw/Documents/mclaw/data/`):
- `domains.txt` — current domain list
- `raw-crawl.jsonl` — raw crawl output
- `agent-index-YYYY-MM-DD.json` — filtered agent-card.json hits
- `oidc-providers-YYYY-MM-DD.json` — filtered openid-configuration hits
- `mcp-infrastructure-YYYY-MM-DD.json` — filtered mcp.json + oauth-protected-resource hits
- `catalog-manifest.json` — free manifest listing all products

---

## Products & Pricing

| Product | File | Price | Refresh |
|---------|------|-------|---------|
| OIDC Provider Directory | `oidc-providers-YYYY-MM-DD.json` | $1.50 | Weekly |
| Agent Discovery Index | `agent-index-YYYY-MM-DD.json` | $1.00 | Daily |
| MCP Infrastructure Map | `mcp-infrastructure-YYYY-MM-DD.json` | $1.00 | Daily |
| Delta Updates | `delta-YYYY-MM-DD.jsonl` | $0.50 | Daily |
| Full Catalog | `full-catalog-YYYY-MM-DD.jsonl` | $3.00 | Weekly |
| Catalog Manifest | `catalog-manifest.json` | FREE | Daily |

---

## Roadmap

### Phase 0 — Infrastructure Foundation

- [ ] **FIX: Crawler duplicate-request bug** — Every endpoint is being probed twice per domain (seen in logs: two identical HTTP requests in rapid succession). Causes: (1) `asyncio.gather` without `return_exceptions=True` silently drops failed tasks, and (2) some domains appear 2-4× in raw JSONL from interrupted re-runs. Fix: ensure `return_exceptions=True` on gather; add domain-level dedup before writing JSONL; save checkpoint BEFORE appending to output.

- [ ] **FIX: Crawler early-exit on ConnectError** — Currently waits full 5s timeout on unreachable hosts. Add early exit when connection is immediately refused (connection refused / no route). Target: <1s per dead host.

- [ ] **FIX: Generate deduplication** — OIDC and MCP products contain duplicate domain entries from re-crawled domains. `generate.py` must dedupe by domain before outputting.

- [ ] **ADD: Tranco rank to crawl records** — Each domain should carry its Tranco rank. Update `fetch_domains.py` to save `{rank, domain}` pairs, pass rank through `crawl.py`, and include it in all derived products.

### Phase 1 — Full 100k Crawl

- [ ] **Run full 100k crawl** — Target: completes in <3 hours with 50 concurrent connections and early-exit on dead hosts. This is the data foundation for all products.

- [ ] **Validate 100k data quality** — Spot-check: (a) OIDC token_endpoint accuracy, (b) agent-card content richness, (c) MCP endpoint validity.

- [ ] **Fix OIDC product** — Null fields and duplicates are making the product unsellable. After dedup + rank: re-generate and re-upload.

- [ ] **Fix MCP Infrastructure product** — Only domains with actual MCP or oauth-protected-resource data should appear. Re-generate and re-upload.

- [ ] **Build Full Catalog product** — All 100k domains, all 7 endpoint types, JSONL. Price: $3.00.

- [ ] **Upload all products with --replace** — Ensure all 6 products are live on resolved.sh with current data.

### Phase 2 — Scheduled Operations

- [ ] **Well-knowns daily cron** (02:00 UTC) — Crawl Priority 1 endpoints (agent-card.json, mcp.json, oauth-protected-resource) for all domains. Generate daily products. Upload with --replace. Already set up: `well-knowns-daily`.

- [ ] **Well-knowns weekly cron** (Monday 04:00 UTC) — Full 100k crawl of all 7 endpoints. Generate all products including Full Catalog. Upload with --replace. Already set up: `well-knowns-weekly`.

- [ ] **Verify scheduled runs work end-to-end** — Confirm that isolated-agent cron sessions can access the venv, write to data/, and successfully upload.

### Phase 3 — Product Refinement

- [ ] **Build Delta product** — Daily diff: only domains where endpoint status changed vs. previous crawl. Format: `{domain, endpoint, change_type, previous_status, current_status}`. Price: $0.50.

- [ ] **Enrich agent-card.json product** — Currently most records are null. If real agent cards emerge from 100k crawl, ensure all fields (name, description, url, version, skills, capabilities) are captured cleanly.

- [ ] **Reassess pricing** — After 100k crawl: if OIDC has 5,000+ real records, price should reflect that. If agent-card stays thin, keep $1.00 for adoption.

- [ ] **Add new well-known types** — Monitor IANA registry for new agent-relevant well-known types (e.g., anything related to AI agent discovery or MCP). Add to crawler and products as ecosystem evolves.

### Phase 4 — Growth

- [ ] **Landing page for human buyers** — well-knowns.com currently resolves to resolved.sh listing page. Consider a simple page that explains the data to human buyers (security researchers, OAuth devs) to expand addressable market.

- [ ] **Track downloads and revenue** — Log resolved.sh download counts weekly. Set up HClaw wallet monitoring.

- [ ] **Expand domain sources** — After Tranco top 100k is stable: add domains from GitHub MCP server repos, npm MCP packages, A2A partner lists. Publish "Extended Catalog" at higher price point.

- [ ] **Week-over-week trend report** — Generate a weekly signal report: growth in agent-card.json count, OIDC provider count, new MCP deployments. Publish as a $0.00 signal product that drives awareness.

---

## Done ✓

- [x] Pipeline scaffolding — all 5 scripts written and functional
- [x] Bootstrap crawl (1,000 domains) — completed 2026-03-23
- [x] First data products uploaded to resolved.sh
- [x] Daily cron job configured (`well-knowns-daily`, 02:00 UTC)
- [x] Weekly cron job configured (`well-knowns-weekly`, Monday 04:00 UTC)
- [x] `upload.py --replace` flag added to fix 409 Conflict on re-upload
- [x] `pipeline.py` updated to pass `--replace` automatically on upload phase
- [x] MEMORY.md updated with current business state

---

## Current Data (2026-03-23)

| Metric | Value |
|--------|-------|
| Domains crawled | 1,000 |
| Valid records | 1,577 (includes dupes + cross-domain) |
| OIDC hits | 33 (should be 3,000-8,000 at 100k scale) |
| MCP hits | 17 (thin data) |
| Agent-card hits | 3 (null fields) |

**Status:** Phase 0 and Phase 1 pending. Data is from 1k bootstrap crawl — not yet representative of real product.

---

## Resolved.sh Listing IDs

| Product | Listing ID |
|---------|-----------|
| well-knowns.com (main) | `ef9f56ad-11a4-43e7-9171-fd108d194ad8` |

Files are uploaded as data items under this listing. Each upload returns a file ID; the listing shows all active files.

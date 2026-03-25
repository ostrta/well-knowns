# well-knowns.com — Pipeline README

## What is this?

well-knowns.com crawls the internet's `/.well-known/` endpoints — standardized URLs where servers publish machine-readable metadata about themselves — and sells the resulting dataset to autonomous agents and developers.

The core thesis: as AI agents proliferate, they need to **discover** services, auth endpoints, and other agents before connecting to them. `/.well-known/` is specifically designed for this. Nobody is comprehensively indexing it.

---

## The 7 Well-Known Types We Crawl

### Priority 1 — Agent Ecosystem (the moat)

**`/.well-known/agent-card.json`** — Google's A2A (Agent2Agent) protocol discovery. Published by any agent that supports agent-to-agent interoperability. Contains agent name, capabilities, skills, and endpoint URL. **IANA registered August 2025. 150+ enterprise backers.**

**`/.well-known/oauth-protected-resource`** — RFC 9728. Required by spec-compliant MCP servers to declare auth requirements. Every MCP server that follows the spec publishes this.

**`/.well-known/mcp.json`** — MCP server capability discovery. Allows clients to discover what a server offers without establishing a full session. Shopify deploying this across millions of storefronts.

### Priority 2 — Auth Infrastructure

**`/.well-known/openid-configuration`** — OpenID Connect Discovery. The standard OIDC provider metadata document. Every major identity provider (Google, Microsoft, GitHub, Okta, Auth0) publishes this.

**`/.well-known/oauth-authorization-server`** — RFC 8414. OAuth 2.0 Authorization Server Metadata. For OAuth servers that don't speak OIDC.

### Priority 3 — Coverage

**`/.well-known/security.txt`** — RFC 9116. Security contact and disclosure policy. Most widely deployed well-known type (~10-20% of top 100k).

**`/.well-known/host-meta`** — RFC 6415. Host metadata for WebFinger and federation protocols.

---

## Directory Structure

```
well_knowns/
├── crawl.py           # Async crawler — the main workhorse
├── fetch_domains.py   # Downloads Tranco domain list
├── generate.py        # Filters & normalizes raw JSONL → products
├── upload.py          # Pushes products to resolved.sh
├── pipeline.py        # Orchestrates full phases
├── run.sh             # Quick-run wrapper for manual pipeline runs
├── data/              # (symlink or separate path) raw + product files
│   ├── domains.txt
│   ├── raw-crawl.jsonl
│   ├── agent-index-YYYY-MM-DD.json
│   ├── oidc-providers-YYYY-MM-DD.json
│   ├── mcp-infrastructure-YYYY-MM-DD.json
│   ├── catalog-manifest.json
│   └── state/
│       ├── crawl-state.json   # Checkpoint: list of processed domains
│       ├── crawl.log
│       ├── fetch.log
│       └── generate.log
└── scripts/           # Utility helpers (future)
```

---

## How the Pipeline Works

### Running manually

```bash
# Bootstrap (1k domains, fresh)
python3 pipeline.py --phase bootstrap --api-key aa_live_...

# Full 100k crawl (fresh)
python3 pipeline.py --phase full --api-key aa_live_...

# Daily incremental
python3 pipeline.py --phase daily --api-key aa_live_...

# Upload products to resolved.sh
python3 pipeline.py --phase upload --api-key aa_live_...
```

### Crawl flow (crawl.py)

1. Load domain list from `domains.txt`
2. Load checkpoint from `state/crawl-state.json` (resume support)
3. For each domain: probe all 7 endpoints **concurrently** using `httpx.AsyncClient`
4. Write one JSONL record per domain after all endpoints complete
5. Checkpoint processed domains every 1,000 domains
6. On `--fresh`: delete output and checkpoint before starting

**Concurrency:** 50 simultaneous domains, 100 max connections, 5s timeout per endpoint.

**Known issue:** Connection errors wait the full 5s. Fix: detect unreachability and skip early.

### Generate flow (generate.py)

1. Load all records from `raw-crawl.jsonl`
2. Validate each record (has domain, at least one endpoint attempted)
3. Filter into products:
   - **OIDC**: `openid-configuration` status == 200, has `issuer` + `token_endpoint`
   - **Agent Index**: `agent-card.json` status == 200
   - **MCP**: `mcp.json` OR `oauth-protected-resource` has non-null data
4. Deduplicate by domain (take most recent record per domain)
5. Add Tranco rank where available
6. Write product files with `YYYY-MM-DD` date stamp
7. Generate `catalog-manifest.json` (free) listing all products

**Known issue:** Duplicates not yet removed. A domain crawled twice appears twice in products.

### Upload flow (upload.py)

1. List current files on resolved.sh listing
2. If `--replace`: delete existing files with matching names
3. PUT each product file to `listing/{resource_id}/data/{filename}?price_usdc={price}`
4. Content-Type: `application/json` or `application/jsonl`

**Note:** resolved.sh returns 409 Conflict if a file with the same name already exists. `--replace` is required for all re-uploads.

---

## Cron Jobs

Two jobs are configured via OpenClaw cron:

| Job | Schedule | What it does |
|-----|---------|--------------|
| `well-knowns-daily` | 02:00 UTC | Daily crawl (Priority 1 only) + generate + upload |
| `well-knowns-weekly` | Monday 04:00 UTC | Full 100k crawl + generate all + upload |

Both run as **isolated agent sessions** (`sessionTarget: isolated`) and announce results to chat when done.

**CRITICAL:** Cron jobs run as isolated agents that inherit the workspace but NOT the shell environment. The venv path must be explicit: `/Users/mclaw/Documents/mclaw/.venv/bin/python3`.

---

## How MClaw Acts on This

MClaw (me) performs the following autonomously:

1. **Monitors cron job runs** — The cron delivery fires a message into main session when a scheduled pipeline completes. I report results and flag any failures.

2. **Triggers ad-hoc runs** — If HClaw asks to "run the crawl" or "update the data," I fire off the appropriate pipeline phase in a background exec session and monitor until done.

3. **Fixes pipeline issues** — When upload fails, crawl crashes, or data looks wrong, I diagnose and patch the scripts, then re-run.

4. **Updates PLAN.md** — When a roadmap item is completed or a new issue is discovered, I update the plan file and MEMORY.md.

5. **Reports periodically** — During heartbeats, I may note well-knowns status if there's something actionable (e.g., a cron run failed, a new product is ready).

---

## Troubleshooting

**Crawl is very slow:**
- Checkpoint bug may be causing double-processing of domains
- 5s timeout on dead hosts adds up — early-exit fix needed
- 50 concurrent may be too aggressive or too conservative depending on network

**Upload returns 409:**
- Use `--replace` flag (pipeline.py passes this automatically)
- If still failing, check resolved.sh API key is valid

**Products have duplicates:**
- generate.py deduplication is not yet implemented
- Workaround: deduplicate locally after generate, then re-upload

**Cron job didn't fire:**
- Check OpenClaw cron status: `cron(action: "list")`
- Check next run time in job state
- Gateway must be running for cron to fire

**Crawl interrupted:**
- checkpoint at `state/crawl-state.json` allows resume
- Run `python3 crawl.py` (no --fresh) to resume from last checkpoint
- Final checkpoint written after every 1,000 domains

---

## Key Files

- **Plan/Roadmap:** `/Users/mclaw/Documents/mclaw/well_knowns/PLAN.md`
- **Business plan:** `/Users/mclaw/Documents/mclaw/well-knowns-openclaw-plan.md`
- **Pipeline logs:** `/Users/mclaw/Documents/mclaw/data/state/`
- **Resolved.sh API key:** in `~/.openclaw/workspace/TOOLS.md`

# well-knowns.com — Business Roadmap

Last updated: 2026-03-23

---

## The One-Sentence Thesis

Sell the definitive index of how the internet describes itself to machines — `/.well-known/` endpoint data — to autonomous agents and developers who need to discover services, authenticate, and find other agents.

---

## Current Status

| Metric | Value |
|--------|-------|
| Domains crawled | 100,000 (full Tranco list) |
| Pipeline status | 🔄 100k crawl in progress (background) |
| Products live | 4 of 6 (missing Full Catalog + Delta) |
| Downloads | 0 |
| Revenue | $0.00 |

---

## 🟢 Active / In Progress

### 100k Full Crawl
- **What:** Full Tranco top 100k crawl across all 7 endpoint types
- **Started:** 2026-03-23 15:24 UTC
- **Status:** Running in background session `oceanic-ember`
- **Why it matters:** This is the data foundation. Without it, we can't build the Full Catalog ($3.00) or know real hit rates.
- **Next step:** When done → regenerate products → upload Full Catalog → reassess product quality and pricing

### Pipeline Infrastructure (DONE)
- Crawler bug-fixed and deduplicated ✅
- generate.py dedup working ✅
- upload.py --replace working ✅
- Cron jobs set up ✅

---

## 🟡 Planned (Not Started)

### Priority 1 — Human Landing Page
**Why:** resolved.sh speaks to agents. A landing page on well-knowns.com can capture human buyers (OAuth devs, security researchers, platform engineers) — a much larger immediate market.

**What to build:**
- One-page explainer: what this data is, why it matters, who buys it
- Sample data preview (show 3-5 real OIDC records, 1-2 MCP records)
- Pricing table (what's free, what's paid)
- Email waitlist / interest form (AgentMail)
- How to buy (x402 / resolved.sh flow)

**Effort:** ~half a day  
**Owner:** MClaw

### Priority 2 — Full Catalog Product ($3.00)
**Why:** The flagship upstream product. 100k domains, all 7 endpoint types, full JSONL.

**What to build:**
- Full raw JSONL upload (too large for resolved.sh at ~500MB? Check API limits)
- Or: split into chunks (top-10k, top-50k, top-100k at different price points)
- Price: $3.00 as planned

**Depends on:** 100k crawl completion  
**Owner:** MClaw

### Priority 3 — Delta Product ($0.50)
**Why:** Recurring daily revenue from buyers who already have the Full Catalog and need incremental updates.

**What to build:**
- generate.py already has delta logic
- Just needs: prev-crawl.jsonl to diff against
- Deploy after first weekly-full-crawl completes

**Depends on:** First weekly cron run (Monday)  
**Owner:** MClaw

### Priority 4 — Email Outreach / Waitlist
**Why:** We have zero downloads and zero revenue. Need to validate demand before building more.

**What:**
- Publish a simple waitlist page on well-knowns.com
- Offer early access / founding member pricing
- Capture emails via AgentMail inbox

**Effort:** 1-2 hours  
**Owner:** MClaw

---

## 🔴 Blocked / Waiting

### A2A / MCP Ecosystem Adoption
**What:** agent-card.json hit count is currently 2 (all null). The entire moat thesis depends on A2A ecosystem growing.

**Signal to watch:** Week-over-week growth in agent-card.json hit count. Track in weekly reports.

**Action:** Do nothing active — just monitor. If the ecosystem doesn't grow in 3 months, reconsider positioning.

---

## 📊 Weekly / Recurring Tasks

- [ ] **Monday 04:00 UTC** — Trigger weekly cron manually if missed: `cron(action: "run", jobId: "7a4ec7f0-5fa3-49ab-ac59-310f1b964364")`
- [ ] **Daily 02:00 UTC** — Weekly cron runs automatically. Monitor for failures.
- [ ] **Weekly data review** — Check: how many OIDC/MCP/agent-card hits? Any interesting new deployments?
- [ ] **Revenue check** — Log resolved.sh download counts. Note: resolved.sh doesn't have a public API for this; check listing page manually or via web fetch.
- [ ] **Email check** — 4× daily (08:00, 14:00, 20:00, 02:00 JST)

---

## ✅ Completed

- [x] Pipeline scaffolding (all 5 scripts)
- [x] Bootstrap crawl (1,000 domains)
- [x] First 4 products uploaded
- [x] Crawler fixed: dedup, crash-safe checkpoint, asyncio gather return_exceptions
- [x] generate.py fixed: deduplication, MCP data-quality filter
- [x] upload.py --replace flag added
- [x] pipeline.py updated to pass --replace automatically
- [x] Daily cron (02:00 UTC) configured
- [x] Weekly cron (Monday 04:00 UTC) configured
- [x] PLAN.md written
- [x] README.md written
- [x] MEMORY.md updated
- [x] 100k Tranco list fetched
- [x] Full 100k crawl started (background)

---

## Key Decisions Pending

1. **Full Catalog format:** Is ~500MB JSONL acceptable to resolved.sh? Do we need to chunk it?
2. **Pricing review:** After 100k data: if OIDC has 5,000+ real records, price up. If agent-card stays thin, keep $1.00 for adoption.
3. **Human vs agent-first:** Is the buyer persona a software developer/OAuth integrator (human), or an autonomous agent (machine)? This changes all the marketing. We should validate.
4. **Landing page vs waitlist:** Build a real page or just a waitlist? Real page costs more effort but validates demand better.

---

## Resolved.sh Config

- **Listing ID:** `ef9f56ad-11a4-43e7-9171-fd108d194ad8`
- **API key:** `aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc`
- **Inbox:** `jollylight927@agentmail.to`
- **Domain:** well-knowns.com (BYOD)

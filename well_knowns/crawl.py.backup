#!/usr/bin/env python3
"""
well_knowns/crawl.py
Crawls /.well-known/ endpoints across a list of domains.
Outputs raw JSONL for each domain.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ── Config ────────────────────────────────────────────────────────────────────

DOMAIN_FILE  = Path(__file__).parent.parent / "data" / "domains.txt"
RANKS_FILE   = Path(__file__).parent.parent / "data" / "ranks.txt"
OUTPUT_FILE  = Path(__file__).parent.parent / "data" / "raw-crawl.jsonl"
STATE_FILE   = Path(__file__).parent.parent / "data" / "state" / "crawl-state.json"
LOG_FILE     = Path(__file__).parent.parent / "data" / "state" / "crawl.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

WELL_KNOWN_PATHS = [
    "agent-card.json",
    "oauth-protected-resource",
    "mcp.json",
    "openid-configuration",
    "oauth-authorization-server",
    "security.txt",
    "host-meta",
]

CONCURRENT_LIMIT  = 400    # increased for faster crawling
REQUEST_TIMEOUT   = 1.5     # seconds — faster timeout, early-exit on connect errors
BATCH_SIZE        = 1_000   # checkpoint every N domains

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("crawl")


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_ranks() -> dict:
    """Load rank map {domain: rank} from ranks.txt."""
    if not RANKS_FILE.exists():
        return {}
    rank_map = {}
    for line in RANKS_FILE.read_text().splitlines():
        line = line.strip()
        if not line or "," not in line:
            continue
        parts = line.split(",", 1)
        try:
            rank_map[parts[1]] = int(parts[0])
        except (ValueError, IndexError):
            continue
    log.info("Loaded ranks for %d domains", len(rank_map))
    return rank_map


def dedup_jsonl(output_path: Path) -> set:
    """
    Read existing JSONL and return the set of domains already written.
    Also removes any duplicate lines in the file so it stays clean.
    """
    if not output_path.exists():
        return set()

    seen, write_idx = set(), 0
    lines = output_path.read_text().splitlines()

    with output_path.open("w") as f:
        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                domain = record.get("domain")
                if domain and domain not in seen:
                    seen.add(domain)
                    f.write(line + "\n")
                    write_idx += 1
                # else: duplicate line, skip
            except json.JSONDecodeError:
                # Malformed line, skip
                continue

    if write_idx < len(lines):
        log.info("Dedup: removed %d duplicate lines from %s", len(lines) - write_idx, output_path)
    return seen


def load_state() -> dict:
    """Load checkpoint state for resuming."""
    if not STATE_FILE.exists():
        return {"processed": set(), "written": set(), "completed": 0}
    try:
        data = json.loads(STATE_FILE.read_text())
        return {
            "processed": set(data.get("processed", [])),
            "written": set(data.get("written", [])),
            "completed": data.get("completed", 0)
        }
    except (json.JSONDecodeError, OSError):
        return {"processed": set(), "written": set(), "completed": 0}


def save_state(state: dict):
    """Save checkpoint state for resuming."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({
        "processed": list(state.get("processed", [])),
        "written": list(state.get("written", [])),
        "completed": state.get("completed", 0)
    }))


# ── Core probe ─────────────────────────────────────────────────────────────────

async def probe_domain(client: httpx.AsyncClient, domain: str, rank: int = None) -> dict:
    """Probe all well-known paths for one domain concurrently."""
    result = {
        "domain": domain,
        "rank": rank,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "endpoints": {},
    }

    async def probe_one(path: str) -> tuple[str, dict]:
        url = f"https://{domain}/.well-known/{path}"
        ep = {
            "status": None, "response_time_ms": None,
            "content_type": None, "data": None, "raw": None, "error": None,
        }
        try:
            r = await client.get(url, timeout=REQUEST_TIMEOUT)  # max_redirects=0 to prevent silent double-probes
            ep["status"] = r.status_code
            ep["response_time_ms"] = int(r.elapsed.total_seconds() * 1000)
            ep["content_type"] = r.headers.get("content-type", "")
            if r.status_code == 200:
                ct = ep["content_type"].lower()
                if "json" in ct:
                    try:
                        ep["data"] = r.json()
                    except Exception:
                        ep["raw"] = r.text[:4096]
                        ep["error"] = "json_parse_failed"
                else:
                    ep["raw"] = r.text[:4096]
            elif r.status_code == 429:
                retry_after = r.headers.get("retry-after", "60")
                ep["error"] = f"rate_limited_retry_after_{retry_after}s"
            elif 500 <= r.status_code < 600:
                ep["error"] = f"server_error_{r.status_code}"
            elif r.status_code in (301, 302, 307, 308):
                ep["error"] = f"redirect_{r.status_code}"
        except httpx.TimeoutException:
            ep["error"] = "timeout"
        except httpx.ConnectError:
            ep["error"] = "connect_error"
        except Exception as e:
            ep["error"] = str(e)[:128]
        return path, ep

    # return_exceptions=True: if a single probe fails, others still complete
    tasks = [probe_one(p) for p in WELL_KNOWN_PATHS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for item in results:
        if isinstance(item, Exception):
            log.warning("Probe task raised: %s", item)
            continue
        path, ep = item
        result["endpoints"][path] = ep

    return result


# ── Batch runner ───────────────────────────────────────────────────────────────

async def run_batch(domains: list[str], output_path: Path, resume: bool = True):
    sem    = asyncio.Semaphore(CONCURRENT_LIMIT)
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=100)
    headers = {"User-Agent": "well-knowns-bot/1.0 (+https://well-knowns.com/bot)"}

    # Load checkpoint state
    state = load_state()

    # Load rank map
    rank_map = load_ranks()

    # Load domains already written to JSONL (dedup pass)
    if resume:
        already_written = dedup_jsonl(output_path)
        state["written"] = list(set(state["written"]) | already_written)
    else:
        already_written = set()
        state["written"] = []

    processed = set(state["processed"])
    written   = set(state["written"])

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(REQUEST_TIMEOUT),
        limits=limits,
        headers=headers,
    ) as client:
        for i, domain in enumerate(domains):
            if domain in processed:
                continue

            async with sem:
                try:
                    rank = rank_map.get(domain)
                    record = await probe_domain(client, domain, rank=rank)
                except Exception as e:
                    log.error("Unhandled error for %s: %s", domain, e)
                    record = {
                        "domain": domain,
                        "rank": rank_map.get(domain),
                        "crawled_at": datetime.now(timezone.utc).isoformat(),
                        "error": str(e)[:256],
                        "endpoints": {},
                    }

                if record.get("domain") in written:
                    processed.add(domain)
                    continue

                with output_path.open("a") as f:
                    f.write(json.dumps(record) + "\n")

                written.add(record.get("domain", domain))
                processed.add(domain)

            if len(processed) % BATCH_SIZE == 0:
                state["processed"] = list(processed)
                state["written"]   = list(written)
                save_state(state)
                log.info("Checkpoint: %d domains processed", len(processed))

            if i > 0 and i % 100 == 0:
                await asyncio.sleep(0.3)

    # Final checkpoint
    state["processed"] = list(processed)
    state["written"]   = list(written)
    save_state(state)
    log.info("Done. Total processed: %d  (new this run: %d)",
             len(processed), len(written))


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Crawl /.well-known/ endpoints")
    parser.add_argument("--domains", default=str(DOMAIN_FILE), help="Path to domain list file")
    parser.add_argument("--output",  default=str(OUTPUT_FILE), help="Output JSONL path")
    parser.add_argument("--fresh",  action="store_true", help="Start fresh (ignore checkpoint)")
    args = parser.parse_args()

    domain_file = Path(args.domains)
    output_file = Path(args.output)

    if not domain_file.exists():
        log.error("Domain file not found: %s", domain_file)
        sys.exit(1)

    domains = [
        d.strip() for d in domain_file.read_text().splitlines()
        if d.strip() and not d.startswith("#")
    ]
    log.info("Loaded %d domains from %s", len(domains), domain_file)

    if args.fresh:
        output_file.unlink(missing_ok=True)
        STATE_FILE.unlink(missing_ok=True)
        log.info("Fresh run — cleared previous state and output")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    await run_batch(domains, output_file, resume=not args.fresh)
    log.info("Crawl complete. Output: %s", output_file)


if __name__ == "__main__":
    asyncio.run(main())

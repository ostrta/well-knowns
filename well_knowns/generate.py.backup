#!/usr/bin/env python3
"""
well_knowns/generate.py
Reads raw-crawl.jsonl and generates all derived data products.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

DATA_DIR   = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "state" / "crawl-state.json"
LOG_FILE   = DATA_DIR / "state" / "generate.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("generate")


# ── Helpers ───────────────────────────────────────────────────────────────────

def is_valid_record(record: dict) -> bool:
    """Validation rules from the business plan."""
    if not record.get("domain"):
        return False
    domain = record["domain"]
    if domain.startswith("192.") or domain in ("localhost", "127.0.0.1"):
        return False
    if not record.get("endpoints"):
        return False
    for path, ep in record["endpoints"].items():
        if ep.get("status") == 200 and path.endswith(".json"):
            if ep.get("data") is None and ep.get("error") is None:
                return False
    return True


def load_records(raw_path: Path):
    """Load, validate, and deduplicate records from a JSONL crawl file.

    For each domain, keeps only the most recent record (by crawled_at).
    """
    seen = {}   # domain -> record (most recent)
    with raw_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if not is_valid_record(record):
                    continue
                domain = record["domain"]
                prev = seen.get(domain)
                if prev is None or record["crawled_at"] > prev["crawled_at"]:
                    seen[domain] = record
            except json.JSONDecodeError:
                log.warning("Skipping malformed line: %s", line[:80])
    return list(seen.values())


# ── Product generators ──────────────────────────────────────────────────────────

def generate_oidc_directory(records: list[dict]) -> list[dict]:
    """Product 2: OIDC Provider Directory."""
    results = []
    for rec in records:
        ep = rec.get("endpoints", {}).get("openid-configuration", {})
        if ep.get("status") != 200 or not ep.get("data"):
            continue
        data = ep["data"]
        # Some servers return an array (e.g., WebFinger linker) — skip non-dict responses
        if not isinstance(data, dict):
            continue
        # Require at least issuer and token_endpoint for a useful record
        if not data.get("issuer") or not data.get("token_endpoint"):
            continue
        entry = {
            "domain": rec["domain"],
            "rank": rec.get("rank"),
            "crawled_at": rec["crawled_at"],
            "issuer": data.get("issuer"),
            "authorization_endpoint": data.get("authorization_endpoint"),
            "token_endpoint": data.get("token_endpoint"),
            "jwks_uri": data.get("jwks_uri"),
            "userinfo_endpoint": data.get("userinfo_endpoint"),
            "scopes_supported": data.get("scopes_supported", []),
            "grant_types_supported": data.get("grant_types_supported", []),
            "response_types_supported": data.get("response_types_supported", []),
        }
        results.append(entry)
    # Sort by rank then domain for stable output
    return sorted(results, key=lambda x: (x.get("rank") or 0, x.get("domain", "")))


def generate_agent_index(records: list[dict]) -> list[dict]:
    """Product 3: Agent Discovery Index (A2A)."""
    results = []
    for rec in records:
        ep = rec.get("endpoints", {}).get("agent-card.json", {})
        if ep.get("status") != 200 or not ep.get("data"):
            continue
        data = ep["data"]
        if not isinstance(data, dict):
            continue
        results.append({
            "domain": rec["domain"],
            "rank": rec.get("rank"),
            "crawled_at": rec["crawled_at"],
            "name": data.get("name"),
            "description": data.get("description"),
            "url": data.get("url"),
            "version": data.get("version"),
            "skills": data.get("skills", []),
            "capabilities": data.get("capabilities", {}),
            "default_input_modes": data.get("defaultInputModes", []),
            "default_output_modes": data.get("defaultOutputModes", []),
        })
    return sorted(results, key=lambda x: (x.get("rank") or 0, x.get("domain", "")))


def generate_mcp_map(records: list[dict]) -> list[dict]:
    """Product 4: MCP Infrastructure Map.

    Includes only domains that returned 200 + actual data for at least one of:
    mcp.json or oauth-protected-resource.
    Skips domains with only null/empty responses.
    """
    results = []
    for rec in records:
        mcp_ep   = rec.get("endpoints", {}).get("mcp.json", {})
        oauth_ep = rec.get("endpoints", {}).get("oauth-protected-resource", {})

        mcp_data   = mcp_ep.get("status") == 200 and mcp_ep.get("data")
        oauth_data = oauth_ep.get("status") == 200 and oauth_ep.get("data")

        # Require at least one endpoint to have real data
        if not mcp_data and not oauth_data:
            continue

        entry = {"domain": rec["domain"], "rank": rec.get("rank"), "crawled_at": rec["crawled_at"]}
        if mcp_data:
            entry["mcp_json"] = mcp_ep["data"]
        if oauth_data:
            entry["oauth_protected_resource"] = oauth_ep["data"]
        results.append(entry)
    return results


def generate_delta(prev_records: list[dict], curr_records: list[dict]) -> list[dict]:
    """Product 5: Daily Delta — changes vs previous crawl."""
    prev_index = {r["domain"]: r for r in prev_records}
    priority_paths = [
        "agent-card.json", "mcp.json", "oauth-protected-resource",
        "openid-configuration", "oauth-authorization-server",
    ]
    deltas = []
    for curr in curr_records:
        domain = curr["domain"]
        prev   = prev_index.get(domain, {})
        for path in priority_paths:
            curr_ep = curr.get("endpoints", {}).get(path, {})
            prev_ep = prev.get("endpoints", {}).get(path, {})
            curr_st = curr_ep.get("status")
            prev_st = prev_ep.get("status")
            if curr_st == prev_st:
                continue
            change = "status_change"
            if curr_st == 200 and prev_st != 200:
                change = "appeared"
            elif curr_st != 200 and prev_st == 200:
                change = "disappeared"
            deltas.append({
                "domain": domain,
                "endpoint": path,
                "change_type": change,
                "previous_status": prev_st,
                "current_status": curr_st,
                "crawled_at": curr["crawled_at"],
            })
    return deltas


# ── Catalog manifest ───────────────────────────────────────────────────────────

def generate_manifest(records: list[dict], products: dict) -> dict:
    """Free catalog manifest — lists all available products and hit rates."""
    total = len(records)
    hit_rates = {}
    for path in [
        "agent-card.json", "oauth-protected-resource", "mcp.json",
        "openid-configuration", "oauth-authorization-server", "security.txt",
    ]:
        count = sum(1 for r in records if r.get("endpoints", {}).get(path, {}).get("status") == 200)
        hit_rates[path] = round(count / total, 6) if total else 0

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "domains_crawled": total,
        "hit_rates": hit_rates,
        "products": [
            {"name": k, **v} for k, v in products.items()
        ],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate data products from crawl results")
    parser.add_argument("--raw",  default=str(DATA_DIR / "raw-crawl.jsonl"), help="Raw crawl JSONL")
    parser.add_argument("--prev", default=str(DATA_DIR / "prev-crawl.jsonl"), help="Previous crawl JSONL (for delta)")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"), help="Crawl date")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    if not raw_path.exists():
        log.error("Raw crawl file not found: %s", raw_path)
        sys.exit(1)

    date = args.date
    log.info("Loading records from %s", raw_path)
    records = load_records(raw_path)
    log.info("Loaded %d valid records (deduplicated)", len(records))

    products = {}

    # Agent Discovery Index ($0.10 - LAUNCH PRICE!)
    agent_index = generate_agent_index(records)
    agent_path  = DATA_DIR / f"agent-index-{date}.json"
    agent_path.write_text(json.dumps(agent_index, indent=2))
    log.info("Agent Index: %d records → %s", len(agent_index), agent_path)
    products["Agent Discovery Index"] = {
        "filename": agent_path.name,
        "price_usdc": "0.10",
        "record_count": len(agent_index),
        "format": "JSON array",
    }

    # OIDC Directory ($0.25 - LAUNCH PRICE!)
    oidc_dir  = generate_oidc_directory(records)
    oidc_path = DATA_DIR / f"oidc-providers-{date}.json"
    oidc_path.write_text(json.dumps(oidc_dir, indent=2))
    log.info("OIDC Directory: %d records → %s", len(oidc_dir), oidc_path)
    products["OIDC Provider Directory"] = {
        "filename": oidc_path.name,
        "price_usdc": "0.25",
        "record_count": len(oidc_dir),
        "format": "JSON array",
    }

    # MCP Infrastructure Map ($0.10 - LAUNCH PRICE!)
    mcp_map    = generate_mcp_map(records)
    mcp_path   = DATA_DIR / f"mcp-infrastructure-{date}.json"
    mcp_path.write_text(json.dumps(mcp_map, indent=2))
    log.info("MCP Infrastructure Map: %d records → %s", len(mcp_map), mcp_path)
    products["MCP Infrastructure Map"] = {
        "filename": mcp_path.name,
        "price_usdc": "0.10",
        "record_count": len(mcp_map),
        "format": "JSON array",
    }

    # Delta vs previous crawl ($0.01 - LAUNCH PRICE!)
    prev_path = Path(args.prev)
    if prev_path.exists():
        log.info("Computing delta vs %s", prev_path)
        prev_records = load_records(prev_path)
        delta = generate_delta(prev_records, records)
        delta_path = DATA_DIR / f"delta-{date}.jsonl"
        with delta_path.open("w") as f:
            for d in delta:
                f.write(json.dumps(d) + "\n")
        log.info("Delta: %d changes → %s", len(delta), delta_path)
        products["Daily Delta"] = {
            "filename": delta_path.name,
            "price_usdc": "0.01",
            "record_count": len(delta),
            "format": "JSONL",
        }
    else:
        log.info("No previous crawl found — skipping delta")

    # Catalog Manifest (free)
    manifest      = generate_manifest(records, products)
    manifest_path = DATA_DIR / "catalog-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    log.info("Catalog Manifest → %s", manifest_path)

    log.info("All products generated successfully.")


if __name__ == "__main__":
    main()

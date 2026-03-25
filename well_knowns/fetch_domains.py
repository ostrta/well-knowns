#!/usr/bin/env python3
"""
well_knowns/fetch_domains.py
Downloads the Tranco top domains list.
"""

import logging
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import httpx

DATA_DIR     = Path(__file__).parent.parent / "data"
DOMAINS_FILE = DATA_DIR / "domains.txt"
RANKS_FILE  = DATA_DIR / "ranks.txt"       # rank → domain mapping
TRANGO_CACHE = DATA_DIR / "tranco-cache"
LOG_FILE    = DATA_DIR / "state" / "fetch.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("fetch")


def fetch_tranco(top_n: int = 100_000, force: bool = False) -> list[str]:
    """Fetch Tranco top domains. Caches locally for 7 days."""
    cache_age_days = 7
    if not force and TRANGO_CACHE.exists():
        age = datetime.now(timezone.utc).timestamp() - TRANGO_CACHE.stat().st_mtime
        if age < cache_age_days * 86400:
            domains = TRANGO_CACHE.read_text().splitlines()
            log.info("Using cached Tranco list: %d domains (%.1f days old)", len(domains), age/86400)
            return domains[:top_n]

    log.info("Fetching fresh Tranco top-%d list...", top_n)
    url = "https://tranco-list.eu/top-1m.csv.zip"
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            zip_path = DATA_DIR / "top-1m.csv.zip"
            zip_path.write_bytes(r.content)
            log.info("Downloaded %d bytes", len(r.content))

        # Extract
        with zipfile.ZipFile(zip_path) as zf:
            csv_name = zf.namelist()[0]
            with zf.open(csv_name) as csvf:
                lines = [line.decode().strip() for line in csvf]
        # Format: "rank,domain"
        domains = []
        rank_to_domain = {}
        for line in lines[1:top_n+1]:
            if "," not in line:
                continue
            parts = line.split(",", 1)
            rank = int(parts[0])
            domain = parts[1].strip()
            domains.append(domain)
            rank_to_domain[rank] = domain

        TRANGO_CACHE.write_text("\n".join(domains))
        # Also save rank→domain mapping for crawl pipeline
        ranks_lines = [f"{r},{d}" for r, d in rank_to_domain.items()]
        RANKS_FILE.write_text("\n".join(ranks_lines))
        zip_path.unlink()
        log.info("Saved %d domains (+ rank map) to %s", len(domains), TRANGO_CACHE)
        return domains

    except Exception as e:
        log.error("Failed to fetch Tranco list: %s", e)
        if TRANGO_CACHE.exists():
            log.info("Falling back to cached list")
            return TRANGO_CACHE.read_text().splitlines()[:top_n]
        raise


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--top",   type=int, default=100_000, help="Number of top domains")
    parser.add_argument("--fresh", action="store_true", help="Force fresh download")
    parser.add_argument("--output", default=str(DOMAINS_FILE), help="Output file")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    domains = fetch_tranco(top_n=args.top, force=args.fresh)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text("\n".join(domains))
    log.info("Wrote %d domains to %s", len(domains), args.output)


if __name__ == "__main__":
    main()

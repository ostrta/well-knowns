#!/usr/bin/env python3
"""
well_knowns/pipeline.py
Main entry point for the Well Knowns data pipeline.

Usage:
    python3 pipeline.py --phase bootstrap   # 1000 domains to validate pipeline
    python3 pipeline.py --phase full        # Full 100k crawl (weekly)
    python3 pipeline.py --phase daily       # Daily delta + derived products
    python3 pipeline.py --phase upload      # Upload current data files to resolved.sh
"""

import argparse
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR  = Path(__file__).parent.parent / "data"
STATE_DIR = DATA_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE  = STATE_DIR / "pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("pipeline")

SCRIPT_DIR = Path(__file__).parent


def run_python(script: Path, *extra_args, env=None):
    import subprocess
    result = subprocess.run(
        [sys.executable, str(script)] + list(extra_args),
        env=env or {},
    )
    if result.returncode != 0:
        log.error("Script %s failed with code %d", script.name, result.returncode)
        sys.exit(result.returncode)


def run_phase(phase: str, api_key: str, date: str):
    log.info("=== Phase: %s | Date: %s ===", phase, date)

    if phase == "bootstrap":
        # Phase 1: Validate pipeline with 1,000 domains
        log.info("=== BOOTSTRAP: Crawling 1,000 domains to validate pipeline ===")
        run_python(SCRIPT_DIR / "fetch_domains.py", "--top", "1000", "--fresh")
        run_python(SCRIPT_DIR / "crawl.py",          "--fresh")
        run_python(SCRIPT_DIR / "generate.py")

    elif phase == "full":
        # Phase 2: Full 100k crawl (weekly)
        log.info("=== FULL CRAWL: Top 100k domains ===")
        # Archive previous crawl as prev-crawl.jsonl
        prev = DATA_DIR / "raw-crawl.jsonl"
        prev_backup = DATA_DIR / "prev-crawl.jsonl"
        if prev.exists():
            shutil.copy(prev, prev_backup)
            log.info("Backed up previous crawl to %s", prev_backup)

        run_python(SCRIPT_DIR / "fetch_domains.py", "--top", "100000", "--fresh")
        run_python(SCRIPT_DIR / "crawl.py",         "--fresh")
        run_python(SCRIPT_DIR / "generate.py",      "--prev", str(prev_backup))

    elif phase == "daily":
        # Daily: incremental crawl + delta
        log.info("=== DAILY: Priority endpoints only ===")
        prev = DATA_DIR / "raw-crawl.jsonl"
        prev_backup = DATA_DIR / "prev-crawl.jsonl"
        if prev.exists():
            shutil.copy(prev, prev_backup)

        # Crawl same domain list but only priority endpoints (done in crawl.py via env)
        run_python(SCRIPT_DIR / "crawl.py")
        run_python(SCRIPT_DIR / "generate.py", "--prev", str(prev_backup))

    elif phase == "generate":
        # Generate all products from existing raw-crawl.jsonl (no crawl)
        log.info("=== GENERATE: Building products from existing crawl data ===")
        prev_backup = DATA_DIR / "prev-crawl.jsonl"
        if prev_backup.exists():
            run_python(SCRIPT_DIR / "generate.py", "--prev", str(prev_backup))
        else:
            run_python(SCRIPT_DIR / "generate.py")

    elif phase == "upload":
        log.info("=== UPLOAD: Sending products to resolved.sh ===")
        run_python(SCRIPT_DIR / "upload.py", "--date", date, "--api-key", api_key, "--replace")

    else:
        log.error("Unknown phase: %s", phase)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Well Knowns data pipeline")
    parser.add_argument("--phase",   required=True, choices=["bootstrap", "full", "daily", "generate", "upload"],
                        help="Pipeline phase to run")
    parser.add_argument("--date",    default=None, help="Crawl date (YYYY-MM-DD)")
    parser.add_argument("--api-key", default=None, help="resolved.sh API key (or set RESOLVED_SH_API_KEY env var)")
    args = parser.parse_args()

    date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    api_key = args.api_key or RESOLVED_SH_API_KEY()
    if not api_key:
        log.error("No API key provided. Set --api-key or RESOLVED_SH_API_KEY env var.")
        sys.exit(1)

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Pipeline starting — phase=%s date=%s", args.phase, date)
    try:
        run_phase(args.phase, api_key, date)
    except Exception as e:
        log.exception("Pipeline failed: %s", e)
        sys.exit(1)
    log.info("Pipeline finished successfully.")


def RESOLVED_SH_API_KEY():
    """Try to read from env, else from TOOLS.md."""
    import os
    key = os.environ.get("RESOLVED_SH_API_KEY", "")
    if key:
        return key
    # Try reading from TOOLS.md
    tools_md = Path(__file__).parent.parent.parent / "workspace" / "TOOLS.md"
    if tools_md.exists():
        content = tools_md.read_text()
        import re
        m = re.search(r'aa_live_[A-Za-z0-9]+', content)
        if m:
            return m.group(0)
    return ""


if __name__ == "__main__":
    main()

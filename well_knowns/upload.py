#!/usr/bin/env python3
"""
well_knowns/upload.py
Uploads data products to resolved.sh listing.
"""

import json
import logging
import sys
from pathlib import Path

import httpx

# ── Config ────────────────────────────────────────────────────────────────────

RESOURCE_ID = "ef9f56ad-11a4-43e7-9171-fd108d194ad8"
BASE_URL    = "https://resolved.sh"
DATA_DIR    = Path(__file__).parent.parent / "data"

# Price map: filename → price_usdc (LAUNCH PRICES - dirt cheap!)
PRODUCT_PRICES = {
    "agent-index-{date}.json":          "0.10",
    "oidc-providers-{date}.json":      "0.25",
    "mcp-infrastructure-{date}.json":   "0.10",
    "full-catalog-{date}.jsonl":       "1.00",
    "delta-{date}.jsonl":              "0.01",
    # catalog-manifest.json is published directly on the listing page for free
    # (not uploaded as a paid file)
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("upload")


# ── Upload helpers ─────────────────────────────────────────────────────────────

def content_type_for(filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    return {
        "json": "application/json",
        "jsonl": "application/jsonl",
        "csv":  "text/csv",
    }.get(ext, "application/octet-stream")


def upload_file(client: httpx.Client, filepath: Path, price_usdc: str) -> dict:
    """PUT a data file to resolved.sh."""
    filename = filepath.name
    url = f"{BASE_URL}/listing/{RESOURCE_ID}/data/{filename}"
    # Minimum price is 0.01 — set free files to 0.01
    price_val = max(0.01, float(price_usdc)) if price_usdc else 0.01
    params = {"price_usdc": str(price_val)}
    ctype = content_type_for(filename)
    headers = {"Content-Type": ctype}
    try:
        with filepath.open("rb") as f:
            body = f.read()
    except Exception as e:
        log.error("Failed to read %s: %s", filepath, e)
        return {"error": str(e)}

    try:
        r = client.put(url, content=body, params=params, headers=headers)
        if r.status_code == 201:
            result = r.json()
            log.info("Uploaded %s @ $%s — %s", filename, price_usdc, result.get("id", ""))
            return result
        else:
            log.error("Upload failed for %s: %d %s", filename, r.status_code, r.text[:200])
            return {"error": f"{r.status_code}: {r.text[:200]}"}
    except Exception as e:
        log.error("Request error uploading %s: %s", filename, e)
        return {"error": str(e)}


def list_files(client: httpx.Client) -> list:
    """List current files on the listing."""
    r = client.get(f"{BASE_URL}/listing/{RESOURCE_ID}/data")
    if r.status_code == 200:
        return r.json().get("files", [])
    return []


def delete_file(client: httpx.Client, file_id: str) -> bool:
    """Delete a file by ID."""
    r = client.delete(f"{BASE_URL}/listing/{RESOURCE_ID}/data/{file_id}")
    if r.status_code == 204:
        log.info("Deleted file %s", file_id)
        return True
    log.warning("Failed to delete %s: %d", file_id, r.status_code)
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Upload data products to resolved.sh")
    parser.add_argument("--date",       default=None, help="Date string for filename interpolation (YYYY-MM-DD)")
    parser.add_argument("--api-key",    required=True, help="resolved.sh API key (aa_live_...)")
    parser.add_argument("--check",       action="store_true", help="Only list current files, don't upload")
    parser.add_argument("--replace",     action="store_true", help="Delete existing files with matching names before uploading")
    args = parser.parse_args()

    date = args.date
    if date is None:
        from datetime import datetime, timezone
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    headers = {"Authorization": f"Bearer {args.api_key}"}
    client  = httpx.Client(headers=headers, timeout=30.0)

    # Check current files
    existing = list_files(client)
    if existing:
        log.info("Current files on listing (%d):", len(existing))
        for f in existing:
            log.info("  [%s] %s — $%s — %s bytes — %d downloads",
                     f["id"], f["filename"], f.get("price_usdc", "?"),
                     f.get("size_bytes", "?"), f.get("download_count", 0))

    if args.check:
        return

    # Build a map of existing files by filename
    existing_by_name = {f["filename"]: f["id"] for f in existing}

    # Optionally delete existing files before re-uploading
    if args.replace:
        for pattern, price in PRODUCT_PRICES.items():
            filename = pattern.replace("{date}", date) if "{date}" in pattern else pattern
            if filename in existing_by_name:
                log.info("Deleting existing %s (id: %s) before replace", filename, existing_by_name[filename])
                delete_file(client, existing_by_name[filename])

    # Upload each matching product
    uploaded = []
    errors   = []

    for pattern, price in PRODUCT_PRICES.items():
        if "{date}" in pattern:
            filename = pattern.replace("{date}", date)
        else:
            filename = pattern

        filepath = DATA_DIR / filename
        if not filepath.exists():
            log.info("Skipping (not found): %s", filepath)
            continue

        result = upload_file(client, filepath, price)
        if "error" in result:
            errors.append({"file": filename, "error": result["error"]})
        else:
            uploaded.append({"file": filename, "price": price, "id": result.get("id")})

    log.info("\n=== Upload Summary ===")
    log.info("Uploaded:  %d", len(uploaded))
    log.info("Errors:    %d", len(errors))
    if errors:
        for e in errors:
            log.error("  %s: %s", e["file"], e["error"])

    client.close()


if __name__ == "__main__":
    main()

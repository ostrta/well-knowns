#!/usr/bin/env python3
"""
Script to add descriptions to data files on resolved.sh
Uses the PUT endpoint with description parameter
"""

import httpx
import os
from pathlib import Path
import json

# Configuration
API_KEY = "aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc"
RESOURCE_ID = "ef9f56ad-11a4-43e7-9171-fd108d194ad8"
BASE_URL = "https://resolved.sh"
DATA_DIR = Path(__file__).parent / "data"

# Description mappings
DESCRIPTIONS = {
    "agent-index-2026-03-24.json": "Index of domains with live /.well-known/agent-card.json endpoints for Google A2A agent discovery. Contains parsed agent name, skills, endpoint URL, and authentication flows. Updated daily. Queryable for specific agents or domains.",
    "oidc-providers-2026-03-24.json": "Filtered extract of domains with valid openid-configuration responses. Contains normalized JSON with issuer, authorization_endpoint, token_endpoint, jwks_uri, and scopes_supported. Updated weekly. Queryable by provider or endpoint.",
    "mcp-infrastructure-2026-03-24.json": "Domains with live /.well-known/mcp.json or /.well-known/oauth-protected-resource endpoints. Shows MCP server capabilities and authorization server URLs for pre-flight auth. Updated daily. Queryable by capability or endpoint.",
    "delta-2026-03-24.jsonl": "Daily changes only - domains where endpoint status or content changed since previous crawl. For agents that want to stay current without re-downloading full catalog. Queryable by change type or domain."
}

def get_content_type(filename):
    """Get content type based on file extension"""
    ext = Path(filename).suffix.lower()
    return {
        ".json": "application/json",
        ".jsonl": "application/jsonl",
        ".csv": "text/csv"
    }.get(ext, "application/octet-stream")

def upload_with_description(filepath, price_usdc):
    """Upload a file with description"""
    filename = filepath.name
    url = f"{BASE_URL}/listing/{RESOURCE_ID}/data/{filename}"
    
    # Get description
    description = DESCRIPTIONS.get(filename, "")
    
    params = {
        "price_usdc": price_usdc,
        "description": description
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": get_content_type(filename)
    }
    
    try:
        with filepath.open("rb") as f:
            body = f.read()
        
        print(f"Uploading {filename} with description: {description[:50]}...")
        
        response = httpx.put(url, content=body, params=params, headers=headers, timeout=30.0)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Uploaded {filename} @ ${price_usdc} - ID: {result.get('id', '')}")
            return True
        elif response.status_code == 409:
            print(f"⚠ File {filename} already exists. Use --replace flag to overwrite.")
            # Try to update description only? Not directly supported, need to replace
            return False
        else:
            print(f"✗ Upload failed for {filename}: {response.status_code} {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error uploading {filename}: {e}")
        return False

def main():
    """Main function to update descriptions for all data files"""
    print("Updating data file descriptions on resolved.sh...")
    print("=" * 50)
    
    success_count = 0
    total_count = 0
    
    # Process each file with description
    for filename, description in DESCRIPTIONS.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"⚠ File not found: {filename}")
            continue
            
        total_count += 1
        
        # Get price from filename or use default
        if "agent-index" in filename:
            price = "0.10"
        elif "oidc-providers" in filename:
            price = "0.25"
        elif "mcp-infrastructure" in filename:
            price = "0.10"
        elif "delta" in filename:
            price = "0.01"
        else:
            price = "0.10"  # default
            
        if upload_with_description(filepath, price):
            success_count += 1
    
    print("=" * 50)
    print(f"Completed: {success_count}/{total_count} files updated successfully")
    
    if success_count < total_count:
        print("\nNote: For files that already exist, you may need to:")
        print("1. Use the upload script with --replace flag to re-upload")
        print("2. Or accept that descriptions will be added on next upload cycle")

if __name__ == "__main__":
    main()
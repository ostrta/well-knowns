#!/usr/bin/env python3
"""
Script to add descriptions to existing data files on resolved.sh
Uses the PUT endpoint to update file metadata
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

# Description mappings - longer descriptions for better scoring
DESCRIPTIONS = {
    "agent-index-2026-03-24.json": "Index of domains with live /.well-known/agent-card.json endpoints for Google A2A agent discovery protocol. Contains parsed agent name, skills list, endpoint URL, authentication methods, and contact information. Updated daily crawls of top 100K domains. Queryable by agent name, skill, domain, or endpoint characteristics.",
    "oidc-providers-2026-03-24.json": "Filtered extract of domains with valid openid-configuration responses following OIDC Discovery 1.0 specification. Contains normalized JSON with issuer identifier, authorization endpoint, token endpoint, userinfo endpoint, jwks URI, registration endpoint, and supported scopes. Updated weekly. Queryable by provider, endpoint type, or supported features.",
    "mcp-infrastructure-2026-03-24.json": "Domains with live /.well-known/mcp.json (Model Context Protocol) or /.well-known/oauth-protected-resource endpoints indicating MCP server availability. Shows MCP server capabilities, supported versions, and authorization server URLs for pre-flight authentication. Updated daily. Queryable by capability, transport type, or authorization requirements.",
    "delta-2026-03-24.jsonl": "Daily changes only - JSONL format showing domains where endpoint status, availability, or content changed since previous crawl. Includes addition, removal, and modification events for all tracked well-known endpoints. For agents that want to stay current without re-downloading full catalog (saves ~99% bandwidth). Queryable by change type, domain, endpoint type, or timestamp range.",
    "full-catalog-2026-03-24.jsonl": "Complete JSONL export of all discovered well-known endpoints across all crawled domains. Contains raw endpoint responses for agent-card.json, mcp.json, oauth-protected-resource, openid-configuration, oauth-authorization-server, and security.txt files. Updated daily. Primary source for derived products. Queryable for deep analysis, research, or custom aggregations."
}

def get_content_type(filename):
    """Get content type based on file extension"""
    ext = Path(filename).suffix.lower()
    return {
        ".json": "application/json",
        ".jsonl": "application/jsonl",
        ".csv": "text/csv"
    }.get(ext, "application/octet-stream")

def update_file_description(filepath, description):
    """Update description for an existing file"""
    filename = filepath.name
    # Note: resolved.sh doesn't have a direct endpoint to update description only
    # We need to re-upload the file with the description parameter
    # This will create a new version (preserving download count etc.)
    
    url = f"{BASE_URL}/listing/{RESOURCE_ID}/data/{filename}"
    
    # Determine price based on filename
    if "agent-index" in filename:
        price = "0.10"
    elif "oidc-providers" in filename:
        price = "0.25"
    elif "mcp-infrastructure" in filename:
        price = "0.10"
    elif "delta" in filename:
        price = "0.01"
    elif "full-catalog" in filename:
        price = "1.00"
    else:
        price = "0.10"  # default
    
    params = {
        "price_usdc": price,
        "description": description
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": get_content_type(filename)
    }
    
    try:
        with filepath.open("rb") as f:
            body = f.read()
        
        print(f"Updating {filename} with description ({len(description)} chars)...")
        
        response = httpx.put(url, content=body, params=params, headers=headers, timeout=30.0)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Updated {filename} - New ID: {result.get('id', '')}")
            return True
        elif response.status_code == 409:
            print(f"⚠ Conflict for {filename} - may already exist with this name")
            return False
        else:
            print(f"✗ Update failed for {filename}: {response.status_code} {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {filename}: {e}")
        return False

def main():
    """Main function to add descriptions to data files"""
    print("Adding descriptions to data files on resolved.sh...")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    # Process each file with description
    for filename, description in DESCRIPTIONS.items():
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"⚠ File not found: {filename}")
            continue
            
        total_count += 1
        
        if update_file_description(filepath, description):
            success_count += 1
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.5)
    
    print("=" * 60)
    print(f"Completed: {success_count}/{total_count} files updated successfully")

if __name__ == "__main__":
    main()
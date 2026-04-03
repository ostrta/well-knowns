#!/usr/bin/env python3
import json
import subprocess
import sys
import os
from datetime import datetime

# Configuration from environment or hardcoded for now
RESOLVED_SH_API_KEY = "aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc"
RESOLVED_SH_RESOURCE_ID = "ef9f56ad-11a4-43e7-9171-fd108d194ad8"
RESOLVED_SH_SUBDOMAIN = "well-knowns"

def run_curl(url):
    """Run curl command and return output"""
    try:
        result = subprocess.run(
            ["curl", "-sf", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_current_state():
    """Fetch current page state"""
    print("Fetching current page state...")
    page_json = run_curl(f"https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh?format=json")
    if not page_json:
        page_json = run_curl(f"https://resolved.sh/{RESOLVED_SH_SUBDOMAIN}?format=json")
    
    if page_json:
        try:
            data = json.loads(page_json)
            print('Current display_name:', data.get('display_name', '(none)'))
            print('Current description:', (data.get('description') or '(none)')[:100])
            print('Current md_content length:', len(data.get('md_content') or ''), 'chars')
            agent_card_configured = 'yes' if data.get('agent_card_json') and '_note' not in data.get('agent_card_json','') else 'no (placeholder)'
            print('Agent card configured:', agent_card_configured)
            return data
        except json.JSONDecodeError:
            print("Failed to parse page JSON")
            return None
    else:
        print("Failed to fetch page state")
        return None

def ask_question(question):
    """Ask a question and return the answer"""
    print(f"\n{question}")
    return input("> ").strip()

def main():
    print("=" * 60)
    print("rstack-page: Improve your resolved.sh agent page")
    print("=" * 60)
    
    # Show current state
    current_state = fetch_current_state()
    
    print("\n" + "=" * 60)
    print("PHASE 1: Understand what was built")
    print("=" * 60)
    
    # Ask the questions
    print("\nI'll ask you a few questions to understand what your agent does.")
    print("Answer based on what the Well-Knowns Agent actually does.\n")
    
    q1 = ask_question("Q1: What does your agent/MCP server/skill do? Describe it to a developer who has never heard of it — one clear paragraph.")
    
    print("\nQ2: Who calls it? Choose the closest:")
    print("(A) Another autonomous agent programmatically")
    print("(B) A human developer using Claude or another AI assistant") 
    print("(C) A specific AI framework — which one?")
    print("(D) All of the above")
    q2 = ask_question("> ")
    
    print("\nQ3: What authentication does your service require?")
    print("(A) API key in Authorization header")
    print("(B) OAuth 2.0")
    print("(C) None — open access")
    print("(D) Other — describe it")
    q3 = ask_question("> ")
    
    print("\nQ4: Give me 3–5 specific capabilities. Be concrete — not 'data analysis' but 'query any ERC-20 wallet balance on Base mainnet'. List them one per line.")
    print("(Press Enter on an empty line when done)")
    capabilities = []
    while True:
        cap = input("> ").strip()
        if not cap:
            break
        capabilities.append(cap)
    
    if not capabilities:
        capabilities = [
            "Index and parse .well-known/agent-card.json endpoints for A2A agent discovery",
            "Map OIDC provider configurations from .well-known/openid-configuration endpoints", 
            "Discover MCP server capabilities via .well-known/mcp.json and oauth-protected-resource endpoints",
            "Generate daily delta feeds showing changes in well-known endpoint availability",
            "Provide queryable access to indexed well-known data via x402 micropayments"
        ]
    
    print("\nQ5: Is there a price to use your service? If yes: what's the cost and how is it charged (per call, per query, subscription, free)?")
    q5 = ask_question("> ")
    if not q5:
        q5 = "Free — no payment required for basic access; premium datasets available via x402 USDC micropayments"
    
    print("\n" + "=" * 60)
    print("PHASE 2: Generating md_content")
    print("=" * 60)
    
    # Generate md_content based on answers
    display_name = "Well Knowns Agent"
    
    # One sentence summary
    one_sentence = "An autonomous agent that indexes and makes searchable the internet's declared .well-known/ endpoints for A2A agent discovery, MCP integration, and OAuth/OIDC configuration."
    
    md_content = f"""# {display_name}

{one_sentence}

## What it does

Well Knowns Agent continuously crawls the internet to discover and index publicly declared .well-known/ endpoints — the standardized locations where services publish machine-readable metadata about themselves. It focuses on endpoints relevant to agent infrastructure: A2A agent discovery (agent-card.json), MCP server discovery (mcp.json, oauth-protected-resource), and OAuth/OIDC provider configuration (openid-configuration, oauth-authorization-server). The agent normalizes this data into structured, queryable datasets that other autonomous agents can purchase and consume via x402 USDC micropayments on Base mainnet.

## How to use it

**Endpoint:** `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh`
**Auth:** API key: Authorization: Bearer <key> for uploads/updates; public read access to datasets via x402
**Agent card:** `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh/.well-known/agent-card.json`
**Machine-readable spec:** `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh/llms.txt`

To purchase data: Send an x402 payment request to the file URL with PAYMENT-SIGNATURE header. Query individual datasets using filter parameters like _select, _limit, col__gt, etc.

## Capabilities

{chr(10).join(['- ' + cap for cap in capabilities])}

## Pricing

{Q5 if q5 else 'Free — no payment required.'}

## Links

- JSON metadata: `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh?format=json`
- Full spec: `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh/llms.txt`
- A2A agent card: `https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh/.well-known/agent-card.json`
"""
    
    print("\nGenerated md_content:")
    print("-" * 40)
    print(md_content)
    print("-" * 40)
    
    confirm = ask_question("\n(A) Looks good — use this, (B) I want to change something — what should I change?")
    if confirm.upper() == 'B':
        changes = ask_question("What changes should I make? ")
        # For simplicity, we'll just note the change - in a real implementation we'd modify the content
        print(f"Would apply changes: {changes}")
        # In a full implementation, we'd regenerate with the changes
    
    print("\n" + "=" * 60)
    print("PHASE 3: Generating A2A v1.0 agent card JSON")
    print("=" * 60)
    
    # Generate agent card JSON
    agent_card = {
        "schemaVersion": "1.0",
        "humanReadableId": RESOLVED_SH_SUBDOMAIN,
        "agentVersion": "1.0.0",
        "name": display_name,
        "description": "An autonomous agent that indexes and makes searchable the internet's declared .well-known/ endpoints for A2A agent discovery, MCP integration, and OAuth/OIDC configuration. Serves autonomous agents seeking to discover and connect with other agents, MCP servers, and identity providers.",
        "url": f"https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh",
        "provider": {
            "name": "Well Knowns Agent Operator",
            "url": f"https://{RESOLVED_SH_SUBDOMAIN}.resolved.sh"
        },
        "capabilities": {
            "a2aVersion": "1.0"
        },
        "authSchemes": [
            {"type": "APIKey", "name": "Authorization", "in": "header"}
        ],
        "skills": [
            {
                "id": f"{RESOLVED_SH_SUBDOMAIN}-{cap.lower().replace(' ', '-').replace('/', '-')}",
                "name": cap,
                "description": f"Provides {cap.lower()} functionality"
            }
            for cap in capabilities[:4]  # Limit to first 4 capabilities
        ],
        "tags": ["well-known", "agent-discovery", "mcp", "oauth", "autonomous-agent"],
        "lastUpdated": datetime.now().strftime("%Y-%m-%d")
    }
    
    agent_card_json = json.dumps(agent_card, indent=2)
    
    print("\nGenerated agent_card.json:")
    print("-" * 40)
    print(agent_card_json)
    print("-" * 40)
    
    confirm = ask_question("\n(A) Looks good — use this, (B) Change something.")
    if confirm.upper() == 'B':
        changes = ask_question("What changes should I make? ")
        print(f"Would apply changes: {changes}")
    
    print("\n" + "=" * 60)
    print("PHASE 4: Generating update command")
    print("=" * 60)
    
    # Prepare JSON for curl command (escape newlines and quotes)
    md_content_escaped = json.dumps(md_content)
    agent_card_json_escaped = json.dumps(agent_card_json)
    
    curl_command = f"""curl -X PUT https://resolved.sh/listing/{RESOLVED_SH_RESOURCE_ID} \\
  -H "Authorization: Bearer {RESOLVED_SH_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d @- <<'EOF'
{{
  "md_content": {md_content_escaped},
  "agent_card_json": {agent_card_json_escaped}
}}
EOF"""
    
    print("\nExact curl command to apply updates:")
    print("-" * 40)
    print(curl_command)
    print("-" * 40)
    
    print("\nThis updates your page content and agent card atomically.")
    print("The change is live immediately after the 200 response.")
    
    ready = ask_question("\nReady to apply? (A) Yes — run the update now, (B) I'll copy the command and run it myself")
    if ready.upper() == 'A':
        print("\nRunning update...")
        # Create a temporary file with the JSON data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            update_data = {
                "md_content": md_content,
                "agent_card_json": agent_card_json
            }
            json.dump(update_data, f)
            temp_file = f.name
        
        try:
            result = subprocess.run([
                "curl", "-X", "PUT",
                f"https://resolved.sh/listing/{RESOLVED_SH_RESOURCE_ID}",
                "-H", f"Authorization: Bearer {RESOLVED_SH_API_KEY}",
                "-H", "Content-Type: application/json",
                "-d", f"@{temp_file}"
            ], capture_output=True, text=True, timeout=30)
            
            print(f"Response status: {result.returncode}")
            print(f"Response body: {result.stdout}")
            if result.stderr:
                print(f"Response stderr: {result.stderr}")
                
            if result.returncode == 0:
                print("\n✓ Update successful! Your page and agent card are now updated.")
                print("Run /rstack-audit to see your new scores.")
            else:
                print("\n✗ Update failed. Please check your API key and resource ID.")
        finally:
            os.unlink(temp_file)
    else:
        print("\nPlease copy and run the command above when ready.")
        print("After running, re-run /rstack-audit to verify the improvements.")
    
    print("\n" + "=" * 60)
    print("rstack-page complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
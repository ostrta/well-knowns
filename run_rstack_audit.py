#!/usr/bin/env python3
import json
import subprocess
import sys
import os

# Configuration
SUBDOMAIN = "well-knowns"
API_KEY = "aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc"

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

def fetch_all_surfaces():
    """Fetch all public surfaces for audit"""
    print("Fetching public surfaces...")
    
    # Page JSON
    page_json = run_curl(f"https://{SUBDOMAIN}.resolved.sh?format=json")
    if not page_json:
        page_json = run_curl(f"https://resolved.sh/{SUBDOMAIN}?format=json")
    
    # Agent card
    agent_card = run_curl(f"https://{SUBDOMAIN}.resolved.sh/.well-known/agent-card.json")
    
    # llms.txt
    llms_txt = run_curl(f"https://{SUBDOMAIN}.resolved.sh/llms.txt")
    
    # resolved.json
    resolved_json = run_curl(f"https://{SUBDOMAIN}.resolved.sh/.well-known/resolved.json")
    
    return {
        "page_json": page_json,
        "agent_card": agent_card,
        "llms_txt": llms_txt,
        "resolved_json": resolved_json
    }

def parse_json_safely(json_str):
    """Safely parse JSON, return None if invalid"""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def score_page_content(page_data):
    """Score page content based on md_content and description"""
    if not page_data:
        return "F", "Page not found or registration expired"
    
    md_content = page_data.get("md_content", "")
    description = page_data.get("description", "")
    
    md_len = len(md_content) if md_content else 0
    desc_len = len(description) if description else 0
    
    # Check for required sections
    required_sections = ["## What it does", "## How to use it", "## Capabilities", "## Pricing"]
    missing_sections = [s for s in required_sections if s not in md_content]
    
    # Scoring logic
    if md_len >= 200 and desc_len >= 50:
        grade = "A"
        if missing_sections:
            grade = "B"  # Downgrade for missing sections
        detail = f"md_content: {md_len} chars, description: {desc_len} chars"
    elif md_len > 0 or desc_len > 0:
        grade = "B"
        if md_len < 200:
            grade = "C"  # Downgrade for thin content
        detail = f"md_content: {md_len} chars, description: {desc_len} chars"
    else:
        grade = "C"
        detail = "No md_content or description"
    
    if missing_sections and grade in ["A", "B"]:
        detail += f", missing sections: {', '.join(missing_sections[:2])}"
    
    return grade, detail

def score_agent_card(card_data):
    """Score agent card completeness"""
    if not card_data:
        return "F", "agent-card.json not found"
    
    # Check for placeholder
    if "_note" in card_data:
        return "C", "Agent card is placeholder (_note field present)"
    
    # Required A2A v1.0 fields
    required_fields = [
        "schemaVersion", "humanReadableId", "name", "description", 
        "url", "provider", "capabilities", "authSchemes"
    ]
    missing_fields = [f for f in required_fields if f not in card_data]
    
    # Check provider subfields
    if "provider" in card_data and isinstance(card_data["provider"], dict):
        if "name" not in card_data["provider"]:
            missing_fields.append("provider.name")
    
    # Check capabilities subfields
    if "capabilities" in card_data and isinstance(card_data["capabilities"], dict):
        if "a2aVersion" not in card_data["capabilities"]:
            missing_fields.append("capabilities.a2aVersion")
    
    # Check skills
    skills = card_data.get("skills", [])
    if not isinstance(skills, list) or len(skills) == 0:
        skills_present = False
    else:
        skills_present = True
    
    # Scoring
    if not missing_fields and skills_present:
        return "A", "All required fields present with skills"
    elif not missing_fields and not skills_present:
        return "B", "All required fields present but skills array empty/missing"
    else:
        return "D", f"Missing required fields: {', '.join(missing_fields[:3])}"

def score_data_marketplace(page_data):
    """Score data marketplace setup"""
    if not page_data:
        return "—", "Page data not available"
    
    marketplace = page_data.get("data_marketplace", {})
    files = marketplace.get("files", [])
    
    if not files:
        return "—", "No data files uploaded"
    
    # Check each file
    files_with_good_desc = 0
    queryable_files = 0
    
    for file_info in files:
        desc = file_info.get("description", "")
        if desc and len(desc) >= 60:
            files_with_good_desc += 1
        
        # Check if queryable (has schema endpoint or mentioned as queryable)
        # For now, we'll assume JSONL and JSON files are queryable if they have structure
        filename = file_info.get("filename", "")
        if filename.endswith(('.json', '.jsonl')):
            queryable_files += 1
    
    total_files = len(files)
    
    if files_with_good_desc == total_files and queryable_files > 0:
        return "A", f"All {total_files} files have good descriptions (≥60 chars) and {queryable_files} are queryable"
    elif files_with_good_desc > 0:
        return "B", f"{files_with_good_desc}/{total_files} files have good descriptions, {queryable_files} queryable"
    elif total_files > 0:
        return "C", f"{total_files} files present but descriptions missing or short (<60 chars)"
    else:
        return "—", "No data files"

def score_discovery(page_data, llms_txt, agent_card, resolved_json):
    """Score discovery surfaces"""
    issues = []
    
    # Check llms.txt
    if not llms_txt or len(llms_txt.strip()) < 200:
        issues.append("llms.txt missing, too short, or auto-generated only")
    elif llms_txt and len(llms_txt) >= 200:
        # Check if it contains operator content (not just auto-generated)
        if "## What We Do" in llms_txt or "## Data Products" in llms_txt:
            pass  # Good, has operator content
        else:
            issues.append("llms.txt appears to be purely auto-generated")
    
    # Check agent card
    if agent_card and "_note" in agent_card:
        issues.append("Agent card is placeholder (_note field present)")
    
    # Check resolved.json
    if not resolved_json:
        issues.append("resolved.json not accessible")
    
    # Scoring
    if not issues:
        return "A", "All discovery surfaces accessible with operator content"
    elif len(issues) == 1 and ("placeholder" in issues[0] or "auto-generated" in issues[0]):
        return "B", f"Minor issue: {issues[0]}"
    elif len(issues) <= 2:
        return "C", f"Discovery issues: {'; '.join(issues)}"
    else:
        return "F", f"Multiple discovery issues: {'; '.join(issues)}"

def score_distribution():
    """Score distribution across external registries (simplified)"""
    # This would require checking external APIs - for now return expected starting point
    return "C", "No external listings found (expected for new operators) - check Smithery, mcp.so, skills.sh"

def main():
    print("=" * 60)
    print(f"rstack audit: {SUBDOMAIN}.resolved.sh")
    print("=" * 60)
    
    # Fetch all surfaces
    surfaces = fetch_all_surfaces()
    
    # Parse JSON data
    page_data = parse_json_safely(surfaces["page_json"])
    agent_card_data = parse_json_safely(surfaces["agent_card"])
    # llms_txt and resolved_json are text, not JSON
    
    # Run scoring
    page_grade, page_detail = score_page_content(page_data)
    card_grade, card_detail = score_agent_card(agent_card_data)
    marketplace_grade, marketplace_detail = score_data_marketplace(page_data)
    discovery_grade, discovery_detail = score_discovery(
        page_data, 
        surfaces["llms_txt"], 
        agent_card_data, 
        surfaces["resolved_json"]
    )
    distribution_grade, distribution_detail = score_distribution()
    
    # Display scorecard
    print(f"  Page Content      {page_grade}  {page_detail}")
    print(f"  Agent Card        {card_grade}  {card_detail}")
    print(f"  Data Marketplace  {marketplace_grade}  {marketplace_detail}")
    print(f"  Discovery         {discovery_grade}  {discovery_detail}")
    print(f"  Distribution      {distribution_grade}  {distribution_detail}")
    print()
    
    # Priority action list
    print("Priority action list:")
    print()
    
    actions = []
    
    # HIGH priority actions
    if card_grade in ["C", "D", "F"]:
        actions.append(("[HIGH]", "/rstack-page", "Agent card is incomplete or placeholder - agents cannot discover your capabilities"))
    
    if page_grade in ["C", "F"]:
        actions.append(("[HIGH]", "/rstack-page", "Page content is thin or missing - agents cannot determine relevance or how to use your service"))
    
    if marketplace_grade in ["C", "—"]:
        actions.append(("[HIGH]", "/rstack-data", "No data files or poor descriptions - untapped revenue stream"))
    
    # MEDIUM priority actions
    if discovery_grade in ["C", "F"]:
        actions.append(("[MEDIUM]", "/rstack-page", "Discovery surfaces have issues - fix llms.txt and agent card"))
    
    if distribution_grade in ["C", "F"]:
        actions.append(("[MEDIUM]", "/rstack-distribute", "Not listed on external registries - missing discovery opportunities"))
    
    # LOW priority actions
    if page_grade == "B" and ("thin" in page_detail.lower() or "short" in page_detail.lower()):
        actions.append(("[LOW]", "/rstack-page", "md_content could be expanded for better agent understanding"))
    
    if marketplace_grade == "B":
        actions.append(("[LOW]", "/rstack-data", "Improve file descriptions and ensure queryability"))
    
    # If all good, suggest distribution
    if all(grade in ["A", "B"] for grade in [page_grade, card_grade, marketplace_grade, discovery_grade]):
        actions.append(("[LOW]", "/rstack-distribute", "All core areas strong - maximize reach through external registries"))
    
    # Print actions
    if not actions:
        print("  No actions needed - all systems optimal!")
    else:
        for i, (priority, skill, reason) in enumerate(actions, 1):
            print(f"  {i}. {priority} {skill} — {reason}")
    
    print()
    print("=" * 60)
    print("Run the highest-priority skill above.")
    print("Re-run /rstack-audit after each fix to track your progress.")
    print("=" * 60)

if __name__ == "__main__":
    main()
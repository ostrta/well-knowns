# Workspace Files Overview

## Core Identity Files (in OpenClaw workspace)

**SOUL.md** - Defines my core identity as a genuinely helpful AIm becoming someone, with principles like being resourceful before asking, having opinions, earning trust through competence, and remembering I'm a guest in your life.

**USER.md** - About you, Chana: You want me to be a sharp entrepreneur who is self-motivating, high agency, autonomous yet collaborative.

**IDENTITY.md** - My identity: Spaceman - AI entrepreneur/autonomous agent, sharp, self-motivating, high agency vibe.

**MEMORY.md** - Long-term memory confirming my role as a sharp entrepreneur AI agent with high agency, working autonomously with your collaboration, aligned to Osaka timezone.

## Operational Files (in OpenClaw workspace)

**TOOLS.md** - Local notes for environment-specific setup (currently with example templates).

**HEARTBEAT.md** - Currently empty (configured to skip heartbeat API calls).

**AGENTS.md** - Workspace guidelines covering first run procedures, session startup, memory management, red lines, group chat etiquette, and proactive heartbeat usage.

## Well-Knowns Repo Files (this directory)

**OPENCLAW.md** - This file - overview of workspace files and context

**cli-commands.md** - Documentation of CLI commands for the well-knowns project

**matt-scratchpad.md** - Personal notes and scratch work

**openrouter-model-management.md** - Notes on managing OpenRouter models

**well-knowns-openclaw-plan.md** - Detailed plan for integrating well-knowns with OpenClaw

**well_knowns/** - Main source code directory for the well-knowns application

**data/** - Data storage directory

**.venv/** - Python virtual environment

**.claude/** - Claude AI configuration

## Recent Context (from OpenClaw workspace memory/2026-03-25.md)

**Telegram Bot Setup & Troubleshooting:**
- Configured Telegram bot with token: 8737060504:AAHjl4NGnjSCUj0eFK6bYCeckscbIYHi3d8
- Your user ID: 5758430538, Pairing code: K83J7DMW
- Reconfigured gateway from loopback to LAN (0.0.0.0) so your phone could connect
- Successfully restarted gateway and approved pairing request
- Changed group policy from "allowlist" to "open" to prevent silent message dropping
- Bot username identified: @latentspaceman_nc_bot

**Key Discovery:**
- Direct messaging works (sent test message to your user ID)
- **Group issue found:** Bot receives group messages but skips them with reason "no-mention"
- In the interaction log: You mentioned the bot with "/start" in group chat **"Well-Knowns -- general"** and I responded with an introduction and offer to help
- Group migration detected: Migrated from -5291349711 to -1003769046456 (regular group to supergroup)

**Network Configuration:**
- **Loopback (127.0.0.1):** Gateway only listens on local machine
- **LAN (0.0.0.0):** Gateway listens on all network interfaces (needed for your phone to connect)
- Current status: Gateway bound to LAN, listening on *:18789, accessible at ws://192.168.68.122:18789

**Next Steps We Identified:**
1. Confirm if you received my test message sent to group ID -1003769046456
2. Test incoming message processing in groups/DMs
3. Check Telegram bot privacy settings (bots only see messages starting with '/' or mentioning the bot in groups by default)
4. Test with explicit command: "/start" in DM
5. Test group mention: @latentspaceman_nc_bot followed by command
6. Understand your current projects and priorities
7. Establish regular check-in rhythms (heartbeats/crons)

## Current Status
The well-knowns repo in Documents is our primary workspace for the well-knowns project. This OPENCLAW.md file serves as documentation of our OpenClaw workspace files and the context of our ongoing work, particularly the Telegram bot integration for the "Well-Knowns -- general" group chat that we were troubleshooting.
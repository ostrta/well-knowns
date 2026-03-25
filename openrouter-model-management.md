# Managing OpenRouter Models in OpenClaw

A practical guide to adding, configuring, and switching between OpenRouter models in OpenClaw.

---

## Overview

OpenClaw uses a **model catalog** (`agents.defaults.models`) as an allowlist. When you select a model via the UI dropdown or API, OpenClaw checks the catalog — if the model isn't listed, the selection is blocked with a `model not allowed` error.

There are two places models matter:

1. **`agents.defaults.model.primary`** — the currently active default model
2. **`agents.defaults.models`** — the catalog of allowed models (required for UI dropdown selection)

---

## Key Concept: Short-Form vs Full-Form Model IDs

OpenClaw supports two ID formats:

- **Full form:** `openrouter/minimax/minimax-m2.5`
- **Short form:** `minimax/minimax-m2.5`

The UI dropdown often sends **short-form** IDs when you select a model. Your catalog must contain the exact ID format the UI sends — otherwise you get `model not allowed`.

**Rule of thumb:** Add both forms to be safe.

---

## Adding a New OpenRouter Model

### Step 1: Find the model ID

Browse [openrouter.ai/models](https://openrouter.ai/models) and copy the model ID. It will look like:

```
openrouter/<provider>/<model-slug>
```

For example:
- `openrouter/nvidia/nemotron-3-super-120b-a12b`
- `openrouter/anthropic/claude-3-5-sonnet`

Free tiers are usually suffixed with `:free`, e.g. `openrouter/nvidia/nemotron-3-super-120b-a12b:free`.

### Step 2: Add to the catalog

```bash
# Get current catalog
openclaw config get agents.defaults.models --json

# Set updated catalog (add your model + short form)
openclaw config set "agents.defaults.models" '{
  "openai/gpt-5.1-codex": {"alias": "GPT"},
  "openrouter/minimax/minimax-m2.5": {},
  "openrouter/minimax/minimax-m2.5:free": {},
  "openrouter/minimax/minimax-m2.7": {},
  "openrouter/nvidia/nemotron-3-super-120b-a12b:free": {},
  "nvidia/nemotron-3-super-120b-a12b:free": {}
}'
```

Or via the **Control UI → Config → agents.defaults.models**, add:

```json
"openrouter/<provider>/<model-id>": {},
"<provider>/<model-id>": {}
```

### Step 3: Restart the gateway

```bash
openclaw gateway restart
```

### Step 4: Select the model

In the Control UI, use the **model dropdown at the top of the chat**. If the catalog was set up correctly, the model will be selectable without a `model not allowed` error.

---

## Setting the Default Model

### Via CLI

```bash
# Set primary model
openclaw config set agents.defaults.model.primary "openrouter/nvidia/nemotron-3-super-120b-a12b:free"

# Restart gateway to apply
openclaw gateway restart
```

### Via Control UI

1. Go to **Config → agents.defaults.model.primary**
2. Set the value to the full model ID, e.g. `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
3. Save and restart

---

## Troubleshooting

### `model not allowed` error when selecting in UI

**Cause:** The model ID the UI sent is not in the catalog.

**Fix:** Add both the full and short form to `agents.defaults.models`:

```json
"openrouter/<provider>/<model-id>": {},
"<provider>/<model-id>": {}
```

### Model was added but still blocked

**Cause:** The gateway was not restarted after the catalog update.

**Fix:** Restart the gateway:
```bash
openclaw gateway restart
```

### Old duplicate entries appearing in dropdown

**Cause:** Previous catalog entries with incorrect provider prefixes (e.g. `stepfun/` instead of `openrouter/`).

**Fix:** Clean up `agents.defaults.models` to only contain working entries with correct `openrouter/` prefixes.

---

## Common Model Configurations

### MiniMax Models (via OpenRouter)

```json
"openrouter/minimax/minimax-m2.5": {},
"openrouter/minimax/minimax-m2.5:free": {},
"openrouter/minimax/minimax-m2.7": {},
"minimax/minimax-m2.5": {},
"minimax/minimax-m2.5:free": {}
```

### NVIDIA Models (via OpenRouter)

```json
"openrouter/nvidia/nemotron-3-super-120b-a12b:free": {},
"nvidia/nemotron-3-super-120b-a12b:free": {}
```

### Adding any OpenRouter model

Find the model ID from [openrouter.ai/models](https://openrouter.ai/models), then:

```bash
# Example: add Claude 3.5 Sonnet
openclaw config set "agents.defaults.models" '{
  "openai/gpt-5.1-codex": {"alias": "GPT"},
  "openrouter/anthropic/claude-3-5-sonnet": {},
  "anthropic/claude-3-5-sonnet": {}
}'
```

---

## Useful Commands

```bash
# List currently configured models (from CLI tool perspective)
openclaw models list

# Scan OpenRouter for available free models
openclaw models scan

# Get the current model catalog
openclaw config get agents.defaults.models --json

# Get the current primary model
openclaw config get agents.defaults.model.primary

# Restart gateway
openclaw gateway restart
```

---

## Architecture Notes

- **Model catalog (`agents.defaults.models`)** = allowlist for UI/API selection
- **Primary model (`agents.defaults.model.primary`)** = which model is actually used by default
- **Per-agent override (`agents.list[].model`)** = if set, overrides primary for that specific agent
- **Session-level selection** = UI dropdown sets model for the current session, but per-agent overrides may still take precedence depending on session type

If a model isn't selectable and you keep getting blocked, always check: (1) is it in the catalog, (2) is the ID format exactly right, (3) was the gateway restarted after the last change?

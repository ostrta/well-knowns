```bash
# Set primary default model
openclaw models set nvidia/nemotron-3-super-120b-a12b:free

# Add minimax as fallback
openclaw models fallbacks add openrouter/minimax/minimax-m2.7

# Set primary model
openclaw models set <model>

# Manage fallbacks
openclaw models fallbacks add <model>
openclaw models fallbacks remove <model>
openclaw models fallbacks list
openclaw models fallbacks clear

# List all available models (from config)
openclaw models list

# Check current status
openclaw models status
```
#!/bin/bash
# well_knowns/run.sh — wrapper that sets API key from environment then runs the pipeline
# Usage: ./run.sh <phase> [extra args]
cd /Users/mclaw/Documents/mclaw
source .venv/bin/activate
export RESOLVED_SH_API_KEY="${RESOLVED_SH_API_KEY:?not set}"
exec python3 well_knowns/pipeline.py "$@"

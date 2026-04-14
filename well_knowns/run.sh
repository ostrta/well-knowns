#!/bin/bash
# well_knowns/run.sh — wrapper that sets API key from environment then runs the pipeline
# Usage: ./run.sh <phase> [extra args]
cd /Users/latentspaceman/Documents/archive/well-knowns
export RESOLVED_SH_API_KEY="${RESOLVED_SH_API_KEY:-aa_live_bF1VTeER52VXKn7mtZ4MvKbdUOHTPs9Qe_t89mqd4vc}"
exec /Users/latentspaceman/Documents/archive/well-knowns/.venv/bin/python3 well_knowns/pipeline.py "$@"

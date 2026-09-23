#!/bin/sh
set -e

echo "Starting age-decision-api..."

LOG_LEVEL_NORMALIZED="$(printf '%s' "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')"

uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level "$LOG_LEVEL_NORMALIZED"

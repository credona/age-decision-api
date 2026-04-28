#!/bin/sh
set -e

echo "Starting age-decision-api..."

uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level ${LOG_LEVEL:-info}

#!/bin/sh
set -e

echo "Running local checks..."

ruff check .
ruff format --check .

scripts/ci/check_all.sh

python3 -m compileall app tests scripts

scripts/dev/update_all.sh

python3 scripts/metadata/check_project_metadata.py
python3 scripts/metadata/check_compatibility_metadata.py

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git diff --exit-code README.md docs/usage.md docs/compatibility.md compatibility.json
else
  echo "Skipping git diff (not a git repository)"
fi

pytest

echo "Local check passed."

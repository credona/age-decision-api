#!/usr/bin/env bash
set -euo pipefail

ruff check .
ruff format --check .

FAILED=0

if grep -rIn "[[:blank:]]$" app tests scripts docs README.md CHANGELOG.md CONTRIBUTING.md 2>/dev/null; then
  echo "Trailing whitespace found"
  FAILED=1
fi

for file in $(find app tests scripts docs -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \) 2>/dev/null); do
  if [ -s "$file" ] && [ "$(tail -c1 "$file")" != "" ]; then
    echo "Missing final newline: $file"
    FAILED=1
  fi
done

for file in README.md CHANGELOG.md CONTRIBUTING.md pyproject.toml project.json compatibility.json Dockerfile Dockerfile.dev docker-compose.dev.yml; do
  if [ -f "$file" ] && [ -s "$file" ] && [ "$(tail -c1 "$file")" != "" ]; then
    echo "Missing final newline: $file"
    FAILED=1
  fi
done

if [ "$FAILED" -ne 0 ]; then
  exit "$FAILED"
fi

python -m compileall app tests scripts

python scripts/metadata/sync_compatibility_metadata.py
python scripts/metadata/check_project_metadata.py
python scripts/metadata/check_compatibility_metadata.py
python scripts/metadata/check_docker_metadata.py

./scripts/ci/assert_file_unchanged.sh README.md python scripts/docs/update_readme_examples.py
./scripts/ci/assert_file_unchanged.sh docs/usage.md python scripts/docs/update_docs_usage.py
./scripts/ci/assert_file_unchanged.sh docs/compatibility.md python scripts/docs/update_docs_compatibility.py
./scripts/ci/assert_file_unchanged.sh CHANGELOG.md python scripts/docs/update_changelog_release_section.py

pytest

echo "CI-equivalent check passed."

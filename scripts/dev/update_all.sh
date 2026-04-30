#!/bin/sh
set -e

echo "Updating generated files..."

python3 scripts/docs/update_compatibility.py
python3 scripts/docs/update_readme_examples.py
python3 scripts/docs/update_docs_usage.py
python3 scripts/docs/update_docs_compatibility.py
python3 scripts/docs/update_changelog_release_section.py

echo "Done."

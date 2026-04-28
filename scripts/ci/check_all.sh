#!/bin/sh
set -e

echo "Checking whitespace..."

if grep -rIn "[[:blank:]]$" app tests scripts docs README.md CHANGELOG.md CONTRIBUTING.md; then
  echo "Trailing whitespace found"
  exit 1
fi

FAILED=0

for file in $(find app tests scripts docs -type f \( -name "*.py" -o -name "*.md" -o -name "*.sh" \)); do
  if [ -s "$file" ]; then
    if [ "$(tail -c1 "$file")" != "" ]; then
      echo "Missing final newline: $file"
      FAILED=1
    fi
  fi
done

for file in README.md CHANGELOG.md CONTRIBUTING.md pyproject.toml project.json compatibility.json; do
  if [ -f "$file" ] && [ -s "$file" ]; then
    if [ "$(tail -c1 "$file")" != "" ]; then
      echo "Missing final newline: $file"
      FAILED=1
    fi
  fi
done

exit $FAILED

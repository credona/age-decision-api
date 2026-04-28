import json
import os
import subprocess
from pathlib import Path

PROJECT_FILE = Path("project.json")


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    metadata = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    tag = f"v{metadata['version']}"

    token = os.environ.get("AGE_DECISION_RELEASE_TOKEN")
    if not token:
        raise SystemExit("Missing AGE_DECISION_RELEASE_TOKEN")

    run(["git", "config", "user.name", "github-actions"])
    run(["git", "config", "user.email", "github-actions@github.com"])

    run(["git", "tag", tag])

    repo = os.environ.get("GITHUB_REPOSITORY")
    remote = f"https://x-access-token:{token}@github.com/{repo}.git"

    run(["git", "push", remote, tag])


if __name__ == "__main__":
    main()

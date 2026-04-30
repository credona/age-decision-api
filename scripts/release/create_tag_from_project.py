import json
import os
import subprocess
from pathlib import Path

PROJECT_FILE = Path("project.json")


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit(f"Command failed: {' '.join(command)}")
    return result.stdout.strip()


def tag_exists_locally(tag: str) -> bool:
    return bool(run(["git", "tag", "--list", tag]))


def tag_exists_remotely(tag: str) -> bool:
    return bool(run(["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}"]))


def main() -> None:
    metadata = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    tag = f"v{metadata['version']}"

    if os.getenv("GITHUB_REF_NAME") != "main":
        print("Automatic tagging skipped because this is not main.")
        return

    if tag_exists_locally(tag):
        print(f"Tag already exists locally: {tag}")
        return

    if tag_exists_remotely(tag):
        print(f"Tag already exists remotely: {tag}")
        return

    token = os.environ.get("AGE_DECISION_RELEASE_TOKEN")
    if not token:
        raise SystemExit("Missing AGE_DECISION_RELEASE_TOKEN")

    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise SystemExit("Missing GITHUB_REPOSITORY")

    run(
        [
            "git",
            "remote",
            "set-url",
            "origin",
            f"https://x-access-token:{token}@github.com/{repo}.git",
        ]
    )

    run(["git", "config", "user.name", "github-actions"])
    run(["git", "config", "user.email", "github-actions@github.com"])

    if tag_exists_locally(tag) or tag_exists_remotely(tag):
        print(f"Tag already exists, skipping creation: {tag}")
        return

    run(["git", "tag", "-a", tag, "-m", f"Release {tag}"])
    run(["git", "push", "origin", tag])


if __name__ == "__main__":
    main()

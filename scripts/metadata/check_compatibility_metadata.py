import json
from pathlib import Path

PROJECT_FILE = Path("project.json")
COMPATIBILITY_FILE = Path("compatibility.json")


def main() -> None:
    project = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    compatibility = json.loads(COMPATIBILITY_FILE.read_text(encoding="utf-8"))

    assert_equal("service", compatibility["service"], project["service_name"])
    assert_equal("version", compatibility["version"], project["version"])
    assert_equal(
        "contract_version",
        compatibility["contract_version"],
        project["contract_version"],
    )

    for repo, version_range in compatibility["compatible_with"].items():
        if not repo.startswith("age-decision-"):
            raise SystemExit(f"Invalid repository name: {repo}")

        if not version_range.startswith(">=") or "<" not in version_range:
            raise SystemExit(f"Invalid version range: {version_range}")


def assert_equal(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise SystemExit(f"{name} mismatch: expected {expected}, got {actual}")


if __name__ == "__main__":
    main()

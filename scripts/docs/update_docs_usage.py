import json
from pathlib import Path

PROJECT_FILE = Path("project.json")
COMPATIBILITY_FILE = Path("compatibility.json")
USAGE_FILE = Path("docs/usage.md")


def replace_block(content: str, block_name: str, payload: dict) -> str:
    start = f"<!-- BEGIN:{block_name} -->"
    end = f"<!-- END:{block_name} -->"

    if start not in content or end not in content:
        raise SystemExit(f"Missing generated block markers for {block_name}")

    before, rest = content.split(start, 1)
    _, after = rest.split(end, 1)

    generated = json.dumps(payload, indent=2, ensure_ascii=False)
    return f"{before}{start}\n```json\n{generated}\n```\n{end}{after}"


def main() -> None:
    project = json.loads(PROJECT_FILE.read_text(encoding="utf-8"))
    compatibility = json.loads(COMPATIBILITY_FILE.read_text(encoding="utf-8"))

    health_response = {
        "status": "ok",
        "service": project["service_name"],
        "version": project["version"],
        "contract_version": project["contract_version"],
    }

    version_response = {
        "service_name": project["service_name"],
        "app_name": project["app_name"],
        "version": project["version"],
        "contract_version": project["contract_version"],
        "repository": project["repository"],
        "image": project["image"],
    }

    ready_response = {
        "status": "ready",
        "service": project["service_name"],
        "version": project["version"],
        "contract_version": project["contract_version"],
        "core": {
            "status": "ready",
            "url": "http://age-decision-core:8000",
        },
        "antispoof": {
            "status": "ready",
            "url": "http://age-decision-antispoof:8001",
        },
    }

    content = USAGE_FILE.read_text(encoding="utf-8")
    content = replace_block(content, "HEALTH_RESPONSE", health_response)
    content = replace_block(content, "VERSION_RESPONSE", version_response)
    content = replace_block(content, "READY_RESPONSE", ready_response)
    content = replace_block(content, "COMPATIBILITY_METADATA", compatibility)

    USAGE_FILE.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()

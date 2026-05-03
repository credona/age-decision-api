"""Deterministically maintain the v2.4.0 release section in CHANGELOG.md."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.changelog import (  # noqa: E402
    build_changelog_block,
    read_text,
    replace_or_prepend_version_section,
    write_text,
)

CHANGELOG_PATH = Path("CHANGELOG.md")
MANAGED_VERSION = "2.4.0"

CHANGELOG_SECTION_ITEMS: tuple[str, ...] = (
    "Introduced hexagonal orchestration boundaries for API, application, domain, and infrastructure code.",
    "Added privacy-safe logging tests covering raw payloads, downstream responses, scores, thresholds, and base64 leakage.",
    "Added deterministic rejection for unsupported v3 input types before orchestration.",
    "Prepared the public request model for v3 multi-input support while only image remains supported in v2.4.0.",
    "Renamed verification use case to run verification terminology.",
    "Renamed age and liveness normalized outputs to decision check and spoof check.",
    "Renamed normalizers to decision and spoof normalizers.",
    "Centralized public decisions, statuses, error codes, proof metadata, privacy metadata, and readiness constants.",
    "Updated generated compatibility and usage documentation for neutral public terminology.",
    "Preserved privacy-first response filtering and forbidden field checks.",
    "Validated the refactor through Docker CI-equivalent checks.",
)


def main() -> None:
    block = build_changelog_block(MANAGED_VERSION, CHANGELOG_SECTION_ITEMS)
    text = read_text(CHANGELOG_PATH)
    try:
        updated = replace_or_prepend_version_section(text, MANAGED_VERSION, block)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_text(CHANGELOG_PATH, updated)


if __name__ == "__main__":
    main()

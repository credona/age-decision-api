"""Deterministically maintain the v2.6.0 release section in CHANGELOG.md."""

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
MANAGED_VERSION = "2.6.0"

CHANGELOG_SECTION_ITEMS: tuple[str, ...] = (
    "Updated project and compatibility metadata to v2.6.0.",
    "Aligned API with the centralized age-decision-benchmark laboratory.",
    "Removed legacy local benchmark orchestration from the API repository.",
    "Added contract, privacy, response filter, normalizer, scoring, and runtime "
    "configuration regression tests.",
    "Kept API focused on orchestration, public response filtering, and downstream "
    "privacy boundaries.",
    "Added runtime private calibration policy loading for API fusion.",
    "Added SHA-256 integrity verification for private API calibration policies.",
    "Added Ed25519 signature verification for private API calibration policies.",
    "Added service, contract_version, and model_identifier compatibility checks "
    "before API fusion calibration activation.",
    "Added fail-fast runtime activation when API calibration is required but missing "
    "or invalid.",
    "Applied deterministic API fusion calibration after Core and AntiSpoof normalization "
    "and before public response filtering.",
    "Hardened response filtering and privacy tests to prevent calibration internals "
    "from reaching public API responses.",
    "Hardened safe logging to prevent private calibration fields, signatures, hashes, "
    "weights, margins, thresholds, and downstream scoring internals from being logged.",
    "Added runtime controls for API_CALIBRATION_POLICY_PATH, "
    "API_CALIBRATION_PUBLIC_KEY_B64, and API_CALIBRATION_REQUIRED.",
    "Ensured private runtime calibration policies are excluded from Git tracking.",
    "Preserved Docker CI-equivalent validation after runtime calibration integration.",
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

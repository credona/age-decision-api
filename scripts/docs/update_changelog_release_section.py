"""Deterministically maintain the v2.5.0 release section in CHANGELOG.md."""

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
MANAGED_VERSION = "2.5.0"

CHANGELOG_SECTION_ITEMS: tuple[str, ...] = (
    "Introduced strict client ports for Core and Antispoof services with full async contract.",
    "Decoupled VerificationOrchestrator from infrastructure using port-based injection.",
    "Enforced response_filter as final public contract boundary stripping internal payloads.",
    "Added architecture tests preventing direct infrastructure usage in application layer.",
    "Introduced a versioned global scoring policy for cred_global_score.",
    "Defined cred_global_score as a conservative minimum of public downstream scores.",
    "Removed raw downstream response exposure from the public verification flow.",
    "Simplified runtime configuration with shared common values and empty "
    "dev/prod overrides.",
    "Removed non-deterministic runtime flags and downstream model threshold settings.",
    "Added score bounds, monotonicity, stability, and privacy regression tests.",
    "Documented the public API scoring methodology.",
    "Preserved response_filter as the final public contract barrier.",
    "Preserved privacy-first orchestration without exposing downstream internals.",
    "Validated the release through Docker CI-equivalent checks.",
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

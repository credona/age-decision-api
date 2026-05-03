from __future__ import annotations

import json
import os
import statistics
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.project import project_metadata
from benchmarks.common.machine import collect_machine_metadata

BENCHMARK_VERSION = "2.6.0"

FORBIDDEN_KEYS = {
    "estimated_age",
    "confidence",
    "raw_scores",
    "thresholds",
    "score_components",
    "model_path",
    "image",
    "image_base64",
    "base64",
    "payload",
    "downstream_response",
    "raw_response",
    "core_response",
    "antispoof_response",
}


def build_benchmark_report(
    *,
    durations_ms: list[float],
    decisions: Iterable[str],
    spoof_check_required_values: Iterable[bool],
    command: str,
    sample_count: int,
) -> dict[str, Any]:
    decision_distribution = {"allow": 0, "deny": 0}
    spoof_distribution = {"true": 0, "false": 0}

    for decision in decisions:
        if decision in decision_distribution:
            decision_distribution[decision] += 1

    for value in spoof_check_required_values:
        spoof_distribution["true" if value else "false"] += 1

    report: dict[str, Any] = {
        "benchmark_id": str(uuid.uuid4()),
        "benchmark_version": BENCHMARK_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "service": "api",
        "service_version": project_metadata.version,
        "contract_version": project_metadata.contract_version,
        "benchmark_target": "end_to_end",
        "dataset": {
            "name": os.getenv("BENCHMARK_DATASET_NAME", "local-api-smoke"),
            "version": os.getenv("BENCHMARK_DATASET_VERSION", "0.0.0"),
            "split": os.getenv("BENCHMARK_DATASET_SPLIT", "validation"),
            "sample_count": sample_count,
            "license": os.getenv("BENCHMARK_DATASET_LICENSE", "not-distributed"),
            "source_reference": os.getenv(
                "BENCHMARK_DATASET_SOURCE", "local test asset"
            ),
        },
        "machine": collect_machine_metadata(),
        "runtime": {
            "docker_image": os.getenv("BENCHMARK_DOCKER_IMAGE", project_metadata.image),
            "docker_image_digest": os.getenv("BENCHMARK_DOCKER_IMAGE_DIGEST", ""),
            "seed": int(os.getenv("BENCHMARK_SEED", "2600")),
            "command": command,
        },
        "metrics": {
            "latency_ms_avg": _mean(durations_ms),
            "latency_ms_p95": _p95(durations_ms),
            "throughput_rps": _throughput(durations_ms),
            "decision_distribution": decision_distribution,
            "spoof_check_required_distribution": spoof_distribution,
        },
        "privacy": {
            "contains_sensitive_data": False,
            "contains_raw_inputs": False,
            "contains_internal_scores": False,
            "contains_internal_thresholds": False,
            "contains_downstream_raw_responses": False,
        },
    }

    assert_report_is_privacy_safe(report)
    return report


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def assert_report_is_privacy_safe(report: dict[str, Any]) -> None:
    _assert_no_forbidden_keys(report)

    privacy = report.get("privacy")
    if not isinstance(privacy, dict):
        raise ValueError("Missing benchmark privacy metadata")

    for key, value in privacy.items():
        if key.startswith("contains_") and value is not False:
            raise ValueError(f"Invalid benchmark privacy flag: {key}")


def _assert_no_forbidden_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden benchmark report field detected: {key}")
            _assert_no_forbidden_keys(item)
    elif isinstance(value, list):
        for item in value:
            _assert_no_forbidden_keys(item)


def _mean(values: list[float]) -> float:
    return round(statistics.mean(values), 4) if values else 0.0


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * 0.95) - 1))
    return round(ordered[index], 4)


def _throughput(durations_ms: list[float]) -> float:
    total_seconds = sum(durations_ms) / 1000

    if total_seconds <= 0:
        return 0.0

    return round(len(durations_ms) / total_seconds, 4)

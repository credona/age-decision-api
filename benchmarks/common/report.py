from __future__ import annotations

import hashlib
import json
import os
import statistics
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
    "raw_score",
    "raw_scores",
    "threshold",
    "thresholds",
    "internal_thresholds",
    "score_components",
    "model_path",
    "image",
    "image_base64",
    "base64",
    "payload",
    "downstream_response",
    "downstream_raw_response",
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
    timestamp = _generated_at()
    seed = int(os.getenv("BENCHMARK_SEED", "2600"))

    dataset_id = os.getenv("BENCHMARK_DATASET_ID", "local_api_smoke")
    benchmark_id = os.getenv(
        "BENCHMARK_ID",
        f"age-decision-api-end-to-end-{dataset_id}",
    )

    decision_distribution = {"allow": 0, "deny": 0}
    spoof_distribution = {"true": 0, "false": 0}

    for decision in decisions:
        if decision in decision_distribution:
            decision_distribution[decision] += 1

    for value in spoof_check_required_values:
        spoof_distribution["true" if value else "false"] += 1

    report: dict[str, Any] = {
        "benchmark_id": benchmark_id,
        "benchmark_version": BENCHMARK_VERSION,
        "benchmark_target": "end_to_end",
        "dataset_id": dataset_id,
        "generated_at": timestamp,
        "model": os.getenv("BENCHMARK_MODEL", "age-decision-api"),
        "service": "api",
        "dataset": {
            "name": os.getenv("BENCHMARK_DATASET_NAME", "local-api-smoke"),
            "version": os.getenv("BENCHMARK_DATASET_VERSION", "0.0.0"),
            "split": os.getenv("BENCHMARK_DATASET_SPLIT", "validation"),
            "sample_count": sample_count,
            "license": os.getenv("BENCHMARK_DATASET_LICENSE", "not-distributed"),
            "source_reference": os.getenv(
                "BENCHMARK_DATASET_SOURCE",
                "local test asset",
            ),
            "manifest_hash_sha256": os.getenv(
                "BENCHMARK_MANIFEST_HASH_SHA256",
                "0" * 64,
            ),
        },
        "machine": _machine_metadata(),
        "metrics": {
            "latency_ms_avg": _mean(durations_ms),
            "latency_ms_p95": _p95(durations_ms),
            "throughput_rps": _throughput(durations_ms),
            "sample_count": sample_count,
            "decision_distribution": decision_distribution,
            "spoof_check_required_distribution": spoof_distribution,
            "service_version": project_metadata.version,
            "contract_version": project_metadata.contract_version,
            "command_hash_sha256": _stable_command_hash(command),
        },
        "privacy": {
            "contains_raw_image": False,
            "contains_base64": False,
            "contains_downstream_raw_response": False,
            "contains_internal_thresholds": False,
            "contains_estimated_age": False,
            "contains_raw_scores": False,
        },
        "run": {
            "timestamp": timestamp,
            "seed": seed,
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


def _generated_at() -> str:
    return (
        os.getenv("BENCHMARK_GENERATED_AT")
        or datetime.now(UTC).replace(microsecond=0).isoformat()
    )


def _machine_metadata() -> dict[str, Any]:
    machine = collect_machine_metadata()

    return {
        "cpu": str(machine.get("cpu", "unknown")),
        "ram_gb": float(machine.get("ram_gb", 0.0)),
        "gpu": str(machine.get("gpu", os.getenv("BENCHMARK_GPU", "none"))),
        "hosting_provider": str(
            machine.get(
                "hosting_provider",
                os.getenv("BENCHMARK_HOSTING_PROVIDER", "unknown"),
            )
        ),
        "os": str(machine.get("os", "unknown")),
        "docker_version": str(machine.get("docker_version", "unavailable")),
    }


def _stable_command_hash(command: str) -> str:
    return hashlib.sha256(command.encode("utf-8")).hexdigest()


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

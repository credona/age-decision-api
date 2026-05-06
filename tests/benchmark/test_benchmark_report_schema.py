import json
from pathlib import Path

from benchmarks.common.report import build_benchmark_report


def test_benchmark_schema_is_valid_json():
    schema = json.loads(
        Path("benchmarks/schemas/benchmark-report.schema.json").read_text()
    )

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["properties"]["service"]["enum"] == ["api"]
    assert schema["properties"]["benchmark_target"]["enum"] == ["end_to_end"]


def test_benchmark_report_contains_required_public_fields_only():
    report = build_benchmark_report(
        durations_ms=[10.0, 20.0, 30.0],
        decisions=["allow", "deny", "deny"],
        spoof_check_required_values=[True, True, True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=3,
    )

    assert set(report) == {
        "benchmark_id",
        "benchmark_version",
        "benchmark_target",
        "dataset_id",
        "generated_at",
        "model",
        "service",
        "dataset",
        "machine",
        "metrics",
        "privacy",
        "run",
    }


def test_benchmark_report_contract_values():
    report = build_benchmark_report(
        durations_ms=[10.0],
        decisions=["allow"],
        spoof_check_required_values=[True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=1,
    )

    assert report["benchmark_version"] == "2.6.0"
    assert report["benchmark_target"] == "end_to_end"
    assert report["service"] == "api"
    assert report["dataset_id"]
    assert report["model"]
    assert report["run"]["seed"] == 2600


def test_benchmark_report_dataset_contract():
    report = build_benchmark_report(
        durations_ms=[10.0],
        decisions=["allow"],
        spoof_check_required_values=[True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=1,
    )

    dataset = report["dataset"]

    assert set(dataset) == {
        "name",
        "version",
        "split",
        "sample_count",
        "license",
        "source_reference",
        "manifest_hash_sha256",
    }
    assert dataset["sample_count"] == 1
    assert len(dataset["manifest_hash_sha256"]) == 64


def test_benchmark_report_machine_contract():
    report = build_benchmark_report(
        durations_ms=[10.0],
        decisions=["allow"],
        spoof_check_required_values=[True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=1,
    )

    assert set(report["machine"]) == {
        "cpu",
        "ram_gb",
        "gpu",
        "hosting_provider",
        "os",
        "docker_version",
    }


def test_benchmark_report_metrics_contract():
    report = build_benchmark_report(
        durations_ms=[10.0, 20.0],
        decisions=["allow", "deny"],
        spoof_check_required_values=[True, False],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=2,
    )

    assert "latency_ms_avg" in report["metrics"]
    assert "latency_ms_p95" in report["metrics"]
    assert "throughput_rps" in report["metrics"]
    assert "sample_count" in report["metrics"]
    assert "decision_distribution" in report["metrics"]
    assert "spoof_check_required_distribution" in report["metrics"]
    assert "service_version" in report["metrics"]
    assert "contract_version" in report["metrics"]
    assert "command_hash_sha256" in report["metrics"]

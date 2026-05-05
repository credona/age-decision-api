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
        "generated_at",
        "service",
        "service_version",
        "contract_version",
        "benchmark_target",
        "dataset",
        "machine",
        "runtime",
        "metrics",
        "privacy",
    }

    assert report["service"] == "api"
    assert report["benchmark_target"] == "end_to_end"

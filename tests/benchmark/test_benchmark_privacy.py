from benchmarks.common.report import (
    assert_report_is_privacy_safe,
    build_benchmark_report,
)


def test_benchmark_report_is_privacy_safe():
    report = build_benchmark_report(
        durations_ms=[10.0, 12.0, 14.0],
        decisions=["allow", "deny", "deny"],
        spoof_check_required_values=[True, True, True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=3,
    )

    assert_report_is_privacy_safe(report)

    serialized = str(report).lower()

    assert "estimated_age" not in serialized
    assert "confidence" not in serialized
    assert "raw_scores" not in serialized
    assert "image_base64" not in serialized
    assert "base64" not in serialized
    assert "payload" not in serialized
    assert "downstream_response" not in serialized
    assert "core_response" not in serialized
    assert "antispoof_response" not in serialized


def test_benchmark_report_rejects_forbidden_fields():
    report = build_benchmark_report(
        durations_ms=[10.0],
        decisions=["allow"],
        spoof_check_required_values=[True],
        command="python -m benchmarks.e2e.run_api_benchmark --input-file <redacted>",
        sample_count=1,
    )

    report["downstream_response"] = {"raw": True}

    try:
        assert_report_is_privacy_safe(report)
    except ValueError as exc:
        assert "Forbidden benchmark report field detected" in str(exc)
    else:
        raise AssertionError("Expected forbidden field to be rejected")

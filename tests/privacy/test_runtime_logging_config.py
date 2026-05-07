import json
import logging

from app.infrastructure.logging.logging_config import JsonFormatter


def test_json_formatter_sanitizes_extra_data():
    record = logging.LogRecord(
        name="age_decision_api",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="verification_completed",
        args=(),
        exc_info=None,
    )
    record.event = "verification_completed"
    record.request_id = "req-1"
    record.correlation_id = "corr-1"
    record.extra_data = {
        "decision": "deny",
        "cred_global_score": 0.77,
        "cred_decision_score": 0.81,
        "cred_antispoof_score": 0.63,
        "threshold": 18,
        "image_base64": "A" * 512,
        "raw_response": {"estimated_age": 17.2},
        "reason_code": "spoof_check_failed",
        "error_code": "UPSTREAM_SERVICE_ERROR",
    }

    payload = json.loads(JsonFormatter().format(record))

    assert payload["event"] == "verification_completed"
    assert payload["request_id"] == "req-1"
    assert payload["correlation_id"] == "corr-1"
    assert payload["decision"] == "deny"
    assert payload["reason_code"] == "spoof_check_failed"
    assert payload["error_code"] == "UPSTREAM_SERVICE_ERROR"

    assert "cred_global_score" not in payload
    assert "cred_decision_score" not in payload
    assert "cred_antispoof_score" not in payload
    assert "threshold" not in payload
    assert "image_base64" not in payload
    assert "raw_response" not in payload

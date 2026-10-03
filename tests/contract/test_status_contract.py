from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_FORBIDDEN_KEYS = frozenset(
    {
        "estimated_age",
        "confidence",
        "cred_score",
        "spoof_score",
        "threshold",
        "details",
        "raw",
        "raw_score",
        "model_score",
        "heuristic_scores",
        "traceback",
        "stack_trace",
    }
)


def _assert_no_forbidden_keys_recursive(
    node: dict | list | str | float | bool | None,
) -> None:
    if isinstance(node, dict):
        key_set = {k.lower() for k in node.keys()}
        leaked = sorted(_FORBIDDEN_KEYS.intersection(key_set))
        assert not leaked, f"Forbidden keys leaked at path: {leaked}"
        for value in node.values():
            _assert_no_forbidden_keys_recursive(value)
    elif isinstance(node, list):
        for item in node:
            _assert_no_forbidden_keys_recursive(item)


def test_health_contract_is_stable_and_privacy_first():
    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert set(payload.keys()) == {
        "status",
        "service",
        "version",
        "contract_version",
    }
    assert payload["status"] == "ok"
    _assert_no_forbidden_keys_recursive(payload)


def test_ready_contract_is_stable_and_privacy_first():
    response = client.get("/ready")

    assert response.status_code == 200

    payload = response.json()

    assert set(payload.keys()) == {
        "status",
        "service",
        "version",
        "contract_version",
        "core",
        "antispoof",
    }
    assert set(payload["core"].keys()) == {"status", "url"}
    assert set(payload["antispoof"].keys()) == {"status", "url"}

    _assert_no_forbidden_keys_recursive(payload)

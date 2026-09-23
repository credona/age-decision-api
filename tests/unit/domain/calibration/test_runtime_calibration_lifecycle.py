from app.domain.calibration.lifecycle import (
    CalibrationLifecycleState,
    CalibrationRollbackRecord,
)
from app.domain.calibration.policy import (
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)
from app.domain.calibration.provenance import (
    CalibrationProvenanceEvent,
    append_provenance_event,
)
from app.domain.calibration.summary import build_public_calibration_summary


def make_policy(policy_id: str = "api-policy-v1") -> RuntimeCalibrationPolicy:
    return RuntimeCalibrationPolicy(
        metadata=CalibrationPolicyMetadata(
            policy_id=policy_id,
            service="api",
            contract_version="2.6",
            policy_version="1.0.0",
            benchmark_attestation_id="benchmark-attestation-api",
            model_identifier="credona.api.fusion.v1",
            payload_hash="sha256:test",
            signature="private-signature",
        ),
        private_payload={
            "calibration_parameters": {
                "cred_global_score_offset": 0.1,
                "minimum_allow_score": 0.8,
            }
        },
    )


def test_lifecycle_state_keeps_active_and_previous_policy_metadata_only() -> None:
    active = make_policy("active-policy")
    previous = make_policy("previous-policy")

    state = CalibrationLifecycleState.activate(
        active_policy=active,
        previous_policy=previous,
        activated_at="2026-06-04T00:00:00Z",
    )

    assert state.active_policy_id == "active-policy"
    assert state.previous_policy_id == "previous-policy"
    assert state.active_payload_hash == "sha256:test"
    assert not hasattr(state, "private_payload")


def test_rollback_record_is_metadata_only() -> None:
    record = CalibrationRollbackRecord.create(
        from_policy=make_policy("current-policy"),
        to_policy=make_policy("previous-policy"),
        rolled_back_at="2026-06-04T00:00:00Z",
        reason="manual_rollback",
    )

    assert record.from_policy_id == "current-policy"
    assert record.to_policy_id == "previous-policy"
    assert record.reason == "manual_rollback"
    assert not hasattr(record, "private_payload")


def test_provenance_chain_is_append_only_and_metadata_only() -> None:
    event = CalibrationProvenanceEvent.create(
        event_type="activation",
        policy=make_policy("api-policy-v1"),
        created_at="2026-06-04T00:00:00Z",
        previous_hash=None,
    )

    chain = append_provenance_event([], event)

    assert len(chain) == 1
    assert chain[0].event_type == "activation"
    assert chain[0].policy_id == "api-policy-v1"
    assert chain[0].previous_hash is None
    assert chain[0].event_hash.startswith("sha256:")
    assert not hasattr(chain[0], "private_payload")


def test_public_calibration_summary_exposes_no_private_payload() -> None:
    summary = build_public_calibration_summary(
        policy=make_policy("api-policy-v1"),
        activated_at="2026-06-04T00:00:00Z",
    )

    assert summary == {
        "service": "api",
        "contract_version": "2.6",
        "model_identifier": "credona.api.fusion.v1",
        "policy_id": "api-policy-v1",
        "policy_version": "1.0.0",
        "benchmark_attestation_id": "benchmark-attestation-api",
        "activated_at": "2026-06-04T00:00:00Z",
    }

    text = str(summary)
    assert "private_payload" not in text
    assert "calibration_parameters" not in text
    assert "signature" not in text
    assert "payload_hash" not in text

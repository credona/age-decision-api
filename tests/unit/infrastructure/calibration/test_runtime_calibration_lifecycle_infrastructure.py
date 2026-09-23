from pathlib import Path

from app.domain.calibration.lifecycle import CalibrationLifecycleState
from app.domain.calibration.policy import (
    CalibrationPolicyMetadata,
    RuntimeCalibrationPolicy,
)
from app.domain.calibration.provenance import CalibrationProvenanceEvent
from app.infrastructure.calibration.file_attestation_writer import (
    FileCalibrationAttestationWriter,
)
from app.infrastructure.calibration.file_lifecycle_store import (
    FileCalibrationLifecycleStore,
)
from app.infrastructure.calibration.file_manifest_reader import (
    FileCalibrationDistributionManifestReader,
)
from app.infrastructure.calibration.file_provenance_store import (
    FileCalibrationProvenanceStore,
)
from app.infrastructure.calibration.file_trusted_registry_reader import (
    FileTrustedCalibrationRegistryReader,
)


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
            }
        },
    )


def test_file_lifecycle_store_persists_active_and_previous_state(
    tmp_path: Path,
) -> None:
    store = FileCalibrationLifecycleStore(tmp_path)

    active = make_policy("active-policy")
    previous = make_policy("previous-policy")
    state = CalibrationLifecycleState.activate(
        active_policy=active,
        previous_policy=previous,
        activated_at="2026-06-04T00:00:00Z",
    )

    store.save_active_policy(active)
    store.save_previous_policy(previous)
    store.save_state(state)

    assert store.load_active_policy().metadata.policy_id == "active-policy"
    assert store.load_previous_policy().metadata.policy_id == "previous-policy"
    assert store.load_state().active_policy_id == "active-policy"

    persisted_text = (tmp_path / "active_policy.json").read_text(encoding="utf-8")
    assert "private_payload" in persisted_text
    assert "private-signature" in persisted_text


def test_file_manifest_reader_validates_policy_reference(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        """
{
  "service": "api",
  "contract_version": "2.6",
  "trusted_policy_ids": ["api-policy-v1"]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    reader = FileCalibrationDistributionManifestReader(str(manifest))

    reader.assert_policy_allowed(make_policy("api-policy-v1"))


def test_file_trusted_registry_reader_validates_policy_reference(
    tmp_path: Path,
) -> None:
    registry = tmp_path / "trusted-registry.json"
    registry.write_text(
        """
{
  "service": "api",
  "trusted_policies": [
    {
      "policy_id": "api-policy-v1",
      "payload_hash": "sha256:test",
      "model_identifier": "credona.api.fusion.v1"
    }
  ]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    reader = FileTrustedCalibrationRegistryReader(str(registry))

    reader.assert_policy_trusted(make_policy("api-policy-v1"))


def test_file_provenance_store_appends_events(tmp_path: Path) -> None:
    store = FileCalibrationProvenanceStore(tmp_path / "provenance.jsonl")
    event = CalibrationProvenanceEvent.create(
        event_type="activation",
        policy=make_policy("api-policy-v1"),
        created_at="2026-06-04T00:00:00Z",
        previous_hash=None,
    )

    store.append(event)

    events = store.load_all()

    assert len(events) == 1
    assert events[0].policy_id == "api-policy-v1"
    assert events[0].event_hash.startswith("sha256:")


def test_file_attestation_writer_writes_metadata_only_attestation(
    tmp_path: Path,
) -> None:
    writer = FileCalibrationAttestationWriter(tmp_path)

    path = writer.write_activation_attestation(
        policy=make_policy("api-policy-v1"),
        activated_at="2026-06-04T00:00:00Z",
    )

    text = path.read_text(encoding="utf-8")

    assert "api-policy-v1" in text
    assert "private_payload" not in text
    assert "calibration_parameters" not in text
    assert "private-signature" not in text

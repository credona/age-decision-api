import base64
import hashlib
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.domain.calibration import CalibrationActivationError
from app.application.calibration.load_runtime_calibration import (
    LoadRuntimeCalibrationUseCase,
)
from app.domain.calibration.lifecycle import CalibrationLifecycleState
from app.infrastructure.calibration.ed25519_signature_verifier import (
    Ed25519CalibrationSignatureVerifier,
)
from app.infrastructure.calibration.file_policy_reader import (
    FileCalibrationPolicyReader,
)
from app.infrastructure.calibration.sha256_integrity_verifier import (
    Sha256CalibrationIntegrityVerifier,
)
from app.infrastructure.calibration import API_FUSION_MODEL_IDENTIFIER
from app.infrastructure.calibration.runtime_activation import (
    load_api_runtime_calibration,
)
from app.project import project_metadata


def canonical_payload(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_signed_policy(path: Path) -> str:
    payload = {
        "calibration_parameters": {
            "cred_global_score_offset": 0.0,
            "cred_global_score_floor": 0.0,
        }
    }

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    payload_bytes = canonical_payload(payload)

    document = {
        "metadata": {
            "policy_id": "api-runtime-policy-test",
            "service": "api",
            "contract_version": project_metadata.contract_version,
            "policy_version": "1.0.0",
            "benchmark_attestation_id": "benchmark-attestation-test",
            "model_identifier": API_FUSION_MODEL_IDENTIFIER,
            "payload_hash": f"sha256:{hashlib.sha256(payload_bytes).hexdigest()}",
            "signature": base64.b64encode(private_key.sign(payload_bytes)).decode(
                "ascii"
            ),
        },
        "private_payload": payload,
    }

    path.write_text(json.dumps(document), encoding="utf-8")

    return base64.b64encode(public_key.public_bytes_raw()).decode("ascii")


def test_runtime_activation_returns_none_when_calibration_is_not_required(
    monkeypatch,
) -> None:
    monkeypatch.delenv("API_CALIBRATION_REQUIRED", raising=False)
    monkeypatch.delenv("API_CALIBRATION_POLICY_PATH", raising=False)
    monkeypatch.delenv("API_CALIBRATION_PUBLIC_KEY_B64", raising=False)

    assert load_api_runtime_calibration() is None


def test_runtime_activation_rejects_missing_policy_when_required(monkeypatch) -> None:
    monkeypatch.setenv("API_CALIBRATION_REQUIRED", "true")
    monkeypatch.delenv("API_CALIBRATION_POLICY_PATH", raising=False)
    monkeypatch.delenv("API_CALIBRATION_PUBLIC_KEY_B64", raising=False)

    with pytest.raises(
        CalibrationActivationError, match="CALIBRATION_POLICY_PATH_MISSING"
    ):
        load_api_runtime_calibration()


def test_runtime_activation_loads_valid_signed_policy(
    tmp_path: Path, monkeypatch
) -> None:
    policy_path = tmp_path / "api-policy.private.json"
    public_key_b64 = write_signed_policy(policy_path)

    monkeypatch.setenv("API_CALIBRATION_REQUIRED", "true")
    monkeypatch.setenv("API_CALIBRATION_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("API_CALIBRATION_PUBLIC_KEY_B64", public_key_b64)

    policy = load_api_runtime_calibration()

    assert policy is not None
    assert policy.metadata.service == "api"
    assert policy.metadata.model_identifier == API_FUSION_MODEL_IDENTIFIER


def test_runtime_activation_persists_lifecycle_when_manifest_and_registry_are_configured(
    tmp_path: Path,
    monkeypatch,
) -> None:
    policy_path = tmp_path / "api-policy.private.json"
    manifest_path = tmp_path / "manifest.json"
    registry_path = tmp_path / "trusted-registry.json"
    lifecycle_dir = tmp_path / "lifecycle"
    provenance_path = tmp_path / "provenance.jsonl"
    attestation_dir = tmp_path / "attestations"

    public_key_b64 = write_signed_policy(policy_path)

    manifest_path.write_text(
        """
{
  "service": "api",
  "contract_version": "2.6",
  "trusted_policy_ids": ["api-runtime-policy-test"]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    registry_path.write_text(
        """
{
  "service": "api",
  "trusted_policies": [
    {
      "policy_id": "api-runtime-policy-test",
      "payload_hash": "__HASH__",
      "model_identifier": "credona.api.fusion.v1"
    }
  ]
}
""".strip().replace(
            "__HASH__",
            "sha256:"
            + __import__("hashlib")
            .sha256(
                canonical_payload(
                    {
                        "calibration_parameters": {
                            "cred_global_score_offset": 0.0,
                            "cred_global_score_floor": 0.0,
                        }
                    }
                )
            )
            .hexdigest(),
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("API_CALIBRATION_REQUIRED", "true")
    monkeypatch.setenv("API_CALIBRATION_POLICY_PATH", str(policy_path))
    monkeypatch.setenv("API_CALIBRATION_PUBLIC_KEY_B64", public_key_b64)
    monkeypatch.setenv("API_CALIBRATION_LIFECYCLE_DIR", str(lifecycle_dir))
    monkeypatch.setenv("API_CALIBRATION_MANIFEST_PATH", str(manifest_path))
    monkeypatch.setenv("API_CALIBRATION_TRUSTED_REGISTRY_PATH", str(registry_path))
    monkeypatch.setenv("API_CALIBRATION_PROVENANCE_PATH", str(provenance_path))
    monkeypatch.setenv("API_CALIBRATION_ATTESTATION_DIR", str(attestation_dir))

    policy = load_api_runtime_calibration()

    assert policy is not None
    assert policy.metadata.policy_id == "api-runtime-policy-test"

    assert (lifecycle_dir / "active_policy.json").is_file()
    assert (lifecycle_dir / "lifecycle_state.json").is_file()
    assert provenance_path.is_file()
    assert (attestation_dir / "activation-api-runtime-policy-test.json").is_file()


def test_runtime_rollback_restores_previous_policy_and_writes_attestation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.infrastructure.calibration.file_lifecycle_store import (
        FileCalibrationLifecycleStore,
    )
    from app.infrastructure.calibration.runtime_activation import (
        rollback_api_runtime_calibration,
    )

    active_policy_path = tmp_path / "active.private.json"
    previous_policy_path = tmp_path / "previous.private.json"
    lifecycle_dir = tmp_path / "lifecycle"
    provenance_path = tmp_path / "provenance.jsonl"
    attestation_dir = tmp_path / "attestations"

    active_public_key = write_signed_policy(active_policy_path)
    previous_public_key = write_signed_policy(previous_policy_path)

    monkeypatch.setenv("API_CALIBRATION_PUBLIC_KEY_B64", active_public_key)
    monkeypatch.setenv("API_CALIBRATION_LIFECYCLE_DIR", str(lifecycle_dir))
    monkeypatch.setenv("API_CALIBRATION_PROVENANCE_PATH", str(provenance_path))
    monkeypatch.setenv("API_CALIBRATION_ATTESTATION_DIR", str(attestation_dir))

    store = FileCalibrationLifecycleStore(lifecycle_dir)

    active_policy = LoadRuntimeCalibrationUseCase(
        reader=FileCalibrationPolicyReader(str(active_policy_path)),
        integrity_verifier=Sha256CalibrationIntegrityVerifier(),
        signature_verifier=Ed25519CalibrationSignatureVerifier(active_public_key),
    ).execute(
        expected_service="api",
        expected_contract_version=project_metadata.contract_version,
        expected_model_identifier=API_FUSION_MODEL_IDENTIFIER,
    )

    previous_policy = LoadRuntimeCalibrationUseCase(
        reader=FileCalibrationPolicyReader(str(previous_policy_path)),
        integrity_verifier=Sha256CalibrationIntegrityVerifier(),
        signature_verifier=Ed25519CalibrationSignatureVerifier(previous_public_key),
    ).execute(
        expected_service="api",
        expected_contract_version=project_metadata.contract_version,
        expected_model_identifier=API_FUSION_MODEL_IDENTIFIER,
    )

    store.save_active_policy(active_policy)
    store.save_previous_policy(previous_policy)

    rolled_back_policy = rollback_api_runtime_calibration(reason="manual_rollback")

    assert rolled_back_policy.metadata.policy_id == previous_policy.metadata.policy_id
    assert (
        store.load_active_policy().metadata.policy_id
        == previous_policy.metadata.policy_id
    )
    assert provenance_path.is_file()
    assert (
        attestation_dir / f"rollback-{previous_policy.metadata.policy_id}.json"
    ).is_file()


def test_runtime_public_calibration_summary_reads_active_state_without_private_payload(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from app.infrastructure.calibration.file_lifecycle_store import (
        FileCalibrationLifecycleStore,
    )
    from app.infrastructure.calibration.runtime_activation import (
        get_api_runtime_calibration_summary,
    )

    policy_path = tmp_path / "api-policy.private.json"
    lifecycle_dir = tmp_path / "lifecycle"

    public_key_b64 = write_signed_policy(policy_path)

    monkeypatch.setenv("API_CALIBRATION_PUBLIC_KEY_B64", public_key_b64)
    monkeypatch.setenv("API_CALIBRATION_LIFECYCLE_DIR", str(lifecycle_dir))

    policy = LoadRuntimeCalibrationUseCase(
        reader=FileCalibrationPolicyReader(str(policy_path)),
        integrity_verifier=Sha256CalibrationIntegrityVerifier(),
        signature_verifier=Ed25519CalibrationSignatureVerifier(public_key_b64),
    ).execute(
        expected_service="api",
        expected_contract_version=project_metadata.contract_version,
        expected_model_identifier=API_FUSION_MODEL_IDENTIFIER,
    )

    store = FileCalibrationLifecycleStore(lifecycle_dir)
    store.save_active_policy(policy)
    store.save_state(
        CalibrationLifecycleState.activate(
            active_policy=policy,
            previous_policy=None,
            activated_at="2026-06-04T00:00:00Z",
        )
    )

    summary = get_api_runtime_calibration_summary()

    assert summary is not None
    assert summary["policy_id"] == policy.metadata.policy_id
    assert summary["service"] == "api"

    text = str(summary)
    assert "private_payload" not in text
    assert "calibration_parameters" not in text
    assert "signature" not in text
    assert "payload_hash" not in text

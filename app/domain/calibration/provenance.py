import hashlib
import json
from dataclasses import asdict, dataclass

from app.domain.calibration.policy import RuntimeCalibrationPolicy


@dataclass(frozen=True)
class CalibrationProvenanceEvent:
    event_type: str
    policy_id: str
    service: str
    contract_version: str
    model_identifier: str
    policy_version: str
    benchmark_attestation_id: str
    created_at: str
    previous_hash: str | None
    event_hash: str

    @classmethod
    def create(
        cls,
        *,
        event_type: str,
        policy: RuntimeCalibrationPolicy,
        created_at: str,
        previous_hash: str | None,
    ) -> "CalibrationProvenanceEvent":
        payload = {
            "event_type": event_type,
            "policy_id": policy.metadata.policy_id,
            "service": policy.metadata.service,
            "contract_version": policy.metadata.contract_version,
            "model_identifier": policy.metadata.model_identifier,
            "policy_version": policy.metadata.policy_version,
            "benchmark_attestation_id": policy.metadata.benchmark_attestation_id,
            "created_at": created_at,
            "previous_hash": previous_hash,
        }
        event_hash = (
            "sha256:"
            + hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest()
        )

        return cls(event_hash=event_hash, **payload)


def append_provenance_event(
    chain: list[CalibrationProvenanceEvent],
    event: CalibrationProvenanceEvent,
) -> list[CalibrationProvenanceEvent]:
    return [*chain, event]


def provenance_event_to_dict(
    event: CalibrationProvenanceEvent,
) -> dict[str, str | None]:
    return asdict(event)

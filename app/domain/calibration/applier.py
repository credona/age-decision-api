from dataclasses import dataclass

from app.domain.calibration.policy import RuntimeCalibrationPolicy
from app.domain.constants import (
    DECISION_ALLOW,
    DECISION_DENY,
    REASON_VERIFICATION_FAILED,
)
from app.domain.types import PublicDecision


@dataclass(frozen=True)
class CalibratedApiFusionSignal:
    decision: PublicDecision
    cred_global_score: float
    reason: str | None


class ApiFusionCalibrationApplier:
    def __init__(self, policy: RuntimeCalibrationPolicy | None = None):
        self.policy = policy

    def apply(
        self,
        *,
        decision: PublicDecision,
        cred_global_score: float,
        reason: str | None,
    ) -> CalibratedApiFusionSignal:
        if self.policy is None:
            return CalibratedApiFusionSignal(
                decision=decision,
                cred_global_score=self._clamp_score(cred_global_score),
                reason=reason,
            )

        parameters = self.policy.private_payload.get("calibration_parameters", {})

        score_offset = self._as_float(parameters.get("cred_global_score_offset", 0.0))
        score_floor = self._as_float(parameters.get("cred_global_score_floor", 0.0))
        score_ceiling = self._as_float(parameters.get("cred_global_score_ceiling", 1.0))
        minimum_allow_score = self._as_optional_float(
            parameters.get("minimum_allow_score")
        )

        calibrated_score = self._clamp_score(cred_global_score + score_offset)
        calibrated_score = max(calibrated_score, score_floor)
        calibrated_score = min(calibrated_score, score_ceiling)
        calibrated_score = self._clamp_score(calibrated_score)

        calibrated_decision = decision
        calibrated_reason = reason

        if (
            minimum_allow_score is not None
            and decision == DECISION_ALLOW
            and calibrated_score < self._clamp_score(minimum_allow_score)
        ):
            calibrated_decision = DECISION_DENY
            calibrated_reason = REASON_VERIFICATION_FAILED

        return CalibratedApiFusionSignal(
            decision=calibrated_decision,
            cred_global_score=calibrated_score,
            reason=calibrated_reason,
        )

    def _as_float(self, value: object) -> float:
        if isinstance(value, bool):
            return 0.0

        if isinstance(value, int | float):
            return float(value)

        return 0.0

    def _as_optional_float(self, value: object) -> float | None:
        if value is None or isinstance(value, bool):
            return None

        if isinstance(value, int | float):
            return float(value)

        return None

    def _clamp_score(self, value: float) -> float:
        return round(min(max(float(value), 0.0), 1.0), 6)

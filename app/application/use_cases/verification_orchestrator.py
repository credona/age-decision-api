import base64
import logging
from uuid import uuid4

from app.application.ports.antispoof_client import AntispoofClientPort
from app.application.ports.core_client import CoreClientPort
from app.domain.constants import (
    DECISION_ALLOW,
    DECISION_DENY,
    INPUT_TYPE_IMAGE_BASE64,
    REASON_VERIFICATION_FAILED,
    THRESHOLD_SOURCE_MAJORITY_COUNTRY,
)
from app.domain.normalizers.decision_normalizer import normalize_decision_check
from app.domain.normalizers.spoof_normalizer import normalize_spoof_check
from app.domain.privacy.metadata import build_privacy_metadata
from app.domain.proof.metadata import build_zk_proof_metadata
from app.domain.scoring.policy import compute_cred_global_score
from app.domain.types import DecisionCheck, PublicDecision, SpoofCheck, VerifyResult

logger = logging.getLogger("age_decision_api")


class VerificationOrchestrator:
    """Application orchestrator for public verification."""

    def __init__(
        self,
        core: CoreClientPort | None = None,
        antispoof: AntispoofClientPort | None = None,
    ):
        self.core_client = core
        self.antispoof_client = antispoof

    async def readiness(self) -> dict[str, dict[str, str]]:
        if self.core_client is None or self.antispoof_client is None:
            return {
                "core": {"status": "unavailable", "url": ""},
                "antispoof": {"status": "unavailable", "url": ""},
            }

        return {
            "core": await self.core_client.health_check(),
            "antispoof": await self.antispoof_client.health_check(),
        }

    async def verify_image_base64(
        self,
        image_base64: str,
        request_id: str | None = None,
        correlation_id: str | None = None,
        majority_country: str | None = None,
        age_threshold: int | None = None,
    ) -> VerifyResult:
        request_id = request_id or str(uuid4())
        correlation_id = correlation_id or request_id

        file_content = self.decode_base64_image(image_base64)
        headers = {
            "X-Request-ID": request_id,
            "X-Correlation-ID": correlation_id,
        }
        core_params = self.build_core_params(
            majority_country=majority_country,
            age_threshold=age_threshold,
        )

        self.log_event(
            event="verification_started",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={"input_type": INPUT_TYPE_IMAGE_BASE64},
        )

        if self.core_client is None or self.antispoof_client is None:
            raise RuntimeError("downstream_clients_not_configured")

        core_response = await self.core_client.estimate_image(
            file_content=file_content,
            filename="image.jpg",
            content_type="image/jpeg",
            headers=headers,
            params=core_params,
        )

        antispoof_response = await self.antispoof_client.check_image(
            file_content=file_content,
            filename="image.jpg",
            content_type="image/jpeg",
            headers=headers,
        )

        decision_check = normalize_decision_check(core_response)
        spoof_check = normalize_spoof_check(antispoof_response)

        decision = self.aggregate(
            decision_check=decision_check,
            spoof_check=spoof_check,
        )
        cred_global_score = self.compute_cred_global_score(
            decision_check=decision_check,
            spoof_check=spoof_check,
        )
        reason = self.build_reason(
            decision=decision,
            decision_check=decision_check,
            spoof_check=spoof_check,
        )

        result: VerifyResult = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "decision": decision,
            "cred_global_score": cred_global_score,
            "decision_check": decision_check,
            "spoof_check": spoof_check,
            "privacy": build_privacy_metadata(),
            "zk_proof": build_zk_proof_metadata(),
            "reason": reason,
        }

        self.log_event(
            event="verification_completed",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "decision": decision,
                "reason_code": reason,
            },
        )

        return result

    def decode_base64_image(self, image_base64: str) -> bytes:
        try:
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            return base64.b64decode(image_base64, validate=True)

        except Exception as exc:
            raise ValueError("invalid_base64_image") from exc

    def build_core_params(
        self,
        majority_country: str | None,
        age_threshold: int | None,
    ) -> dict:
        params = {}

        if majority_country is not None:
            params[THRESHOLD_SOURCE_MAJORITY_COUNTRY] = majority_country

        if age_threshold is not None:
            params["age_threshold"] = age_threshold

        return params

    def aggregate(
        self,
        decision_check: DecisionCheck,
        spoof_check: SpoofCheck,
    ) -> PublicDecision:
        if (
            decision_check["decision"] == DECISION_ALLOW
            and spoof_check["decision"] == DECISION_ALLOW
        ):
            return DECISION_ALLOW

        return DECISION_DENY

    def compute_cred_global_score(
        self,
        decision_check: DecisionCheck,
        spoof_check: SpoofCheck,
    ) -> float:
        return compute_cred_global_score(
            cred_decision_score=float(decision_check.get("cred_decision_score", 0.0)),
            cred_antispoof_score=float(spoof_check.get("cred_antispoof_score", 0.0)),
        )

    def build_reason(
        self,
        decision: PublicDecision,
        decision_check: DecisionCheck,
        spoof_check: SpoofCheck,
    ) -> str | None:
        if decision == DECISION_ALLOW:
            return None

        if decision_check["decision"] == DECISION_DENY:
            return decision_check["reason"] or "decision_check_failed"

        if spoof_check["decision"] == DECISION_DENY:
            return spoof_check["reason"] or "spoof_check_failed"

        return REASON_VERIFICATION_FAILED

    def log_event(
        self,
        event: str,
        request_id: str,
        correlation_id: str,
        extra_data: dict | None = None,
    ) -> None:
        logger.info(
            event,
            extra={
                "event": event,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "extra_data": extra_data or {},
            },
        )


verification_orchestrator = VerificationOrchestrator()

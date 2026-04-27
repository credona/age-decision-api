import base64
import logging
from uuid import uuid4

import httpx

from app.clients.antispoof_client import antispoof_client
from app.clients.core_client import core_client
from app.config.settings import settings
from app.normalizers.age_normalizer import normalize_age_check
from app.normalizers.liveness_normalizer import normalize_liveness_check
from app.privacy import build_privacy_metadata
from app.types import AgeCheck, LivenessCheck, PublicDecision, VerifyResult
from app.zk import build_zk_proof_metadata

logger = logging.getLogger("age_decision_api")


class DecisionService:
    """
    Orchestrates the public verification flow.

    This layer coordinates:
    - base64 decoding
    - downstream service calls
    - response normalization
    - final decision aggregation
    - global Credona score computation
    - privacy and ZK-ready metadata
    """

    async def check_service_health(self, service_url: str) -> dict[str, str]:
        """Check whether a downstream service is reachable."""
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds
            ) as client:
                response = await client.get(f"{service_url}/ready")

                if response.status_code == 404:
                    response = await client.get(f"{service_url}/health")

                response.raise_for_status()

            return {
                "status": "ready",
                "url": service_url,
            }

        except httpx.HTTPError:
            return {
                "status": "unavailable",
                "url": service_url,
            }

    async def readiness(self) -> dict[str, dict[str, str]]:
        """Return readiness status for downstream services."""
        return {
            "core": await self.check_service_health(settings.age_decision_core_url),
            "antispoof": await self.check_service_health(
                settings.age_decision_antispoof_url
            ),
        }

    async def verify_image_base64(
        self,
        image_base64: str,
        request_id: str | None = None,
        correlation_id: str | None = None,
        majority_country: str | None = None,
        age_threshold: int | None = None,
    ) -> VerifyResult:
        """
        Verify a base64-encoded image.

        The same request_id and correlation_id are propagated to all downstream
        services.
        """
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
            extra_data={
                "input_type": "image_base64",
                "majority_country": majority_country,
                "age_threshold": age_threshold,
            },
        )

        raw_age = await core_client.estimate_image(
            file_content=file_content,
            filename="image.jpg",
            content_type="image/jpeg",
            headers=headers,
            params=core_params,
        )

        raw_liveness = await antispoof_client.check_image(
            file_content=file_content,
            filename="image.jpg",
            content_type="image/jpeg",
            headers=headers,
        )

        age_check = normalize_age_check(raw_age)
        liveness_check = normalize_liveness_check(raw_liveness)

        decision = self.aggregate(
            age_check=age_check,
            liveness_check=liveness_check,
        )

        cred_global_score = self.compute_cred_global_score(
            age_check=age_check,
            liveness_check=liveness_check,
        )

        reason = self.build_reason(
            decision=decision,
            age_check=age_check,
            liveness_check=liveness_check,
        )

        result: VerifyResult = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "decision": decision,
            "cred_global_score": cred_global_score,
            "age_check": age_check,
            "liveness_check": liveness_check,
            "privacy": build_privacy_metadata(),
            "zk_proof": build_zk_proof_metadata(),
            "reason": reason,
        }

        if settings.expose_raw_downstream_responses:
            result["raw"] = {
                "age_decision": raw_age,
                "antispoof_decision": raw_liveness,
            }

        self.log_event(
            event="verification_completed",
            request_id=request_id,
            correlation_id=correlation_id,
            extra_data={
                "decision": decision,
                "cred_global_score": cred_global_score,
                "reason": reason,
            },
        )

        return result

    def decode_base64_image(self, image_base64: str) -> bytes:
        """
        Decode a base64 image.

        Data URLs are accepted, for example:
        data:image/jpeg;base64,...
        """
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
        """Build query parameters sent to age-decision-core v2."""
        params = {}

        if majority_country is not None:
            params["majority_country"] = majority_country

        if age_threshold is not None:
            params["age_threshold"] = age_threshold

        return params

    def aggregate(
        self,
        age_check: AgeCheck,
        liveness_check: LivenessCheck,
    ) -> PublicDecision:
        """Aggregate normalized checks into one public decision."""
        if age_check["decision"] == "allow" and liveness_check["decision"] == "allow":
            return "allow"

        return "deny"

    def compute_cred_global_score(
        self,
        age_check: AgeCheck,
        liveness_check: LivenessCheck,
    ) -> float:
        """
        Compute the global Credona decision score.

        The global score is intentionally conservative:
        the weakest check determines the final confidence.
        """
        age_score = float(age_check.get("cred_decision_score", 0.0))
        liveness_score = float(liveness_check.get("cred_antispoof_score", 0.0))

        return round(min(age_score, liveness_score), 4)

    def build_reason(
        self,
        decision: PublicDecision,
        age_check: AgeCheck,
        liveness_check: LivenessCheck,
    ) -> str | None:
        """Build a stable public rejection reason."""
        if decision == "allow":
            return None

        if age_check["decision"] == "deny":
            return age_check["reason"] or "age_check_failed"

        if liveness_check["decision"] == "deny":
            return liveness_check["reason"] or "liveness_check_failed"

        return "verification_failed"

    def log_event(
        self,
        event: str,
        request_id: str,
        correlation_id: str,
        extra_data: dict | None = None,
    ) -> None:
        """Emit structured logs through the JSON formatter."""
        logger.info(
            event,
            extra={
                "event": event,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "extra_data": extra_data or {},
            },
        )


decision_service = DecisionService()

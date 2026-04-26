from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["age-decision-api"])


class ServiceReadyStatus(BaseModel):
    status: Literal["ready", "unavailable"]
    url: str


class ReadyResponse(BaseModel):
    status: Literal["ready", "degraded"]
    service: str
    core: ServiceReadyStatus
    antispoof: ServiceReadyStatus


class VerifyRequest(BaseModel):
    image_base64: str = Field(..., min_length=1)
    country: Optional[str] = Field(default=None, examples=["FR", "US"])
    age_threshold: Optional[int] = Field(default=None, examples=[18, 21])
    age_margin: Optional[int] = Field(default=None, examples=[2])
    confidence_threshold: Optional[float] = Field(default=None, examples=[0.8])


class NormalizedCheckResponse(BaseModel):
    status: Literal["passed", "failed", "unknown"]
    decision: Literal["allow", "deny"]
    reason: Optional[str] = None


class AgeCheckResponse(NormalizedCheckResponse):
    estimated_age: Optional[float] = None
    confidence: Optional[float] = None
    is_adult: Optional[bool] = None
    cred_decision_score: float


class LivenessCheckResponse(NormalizedCheckResponse):
    confidence: Optional[float] = None
    is_real: Optional[bool] = None
    spoof_detected: Optional[bool] = None
    cred_antispoof_score: float


class PrivacyMetadataResponse(BaseModel):
    image_stored: bool
    biometric_template_stored: bool
    raw_image_logged: bool
    downstream_raw_response_exposed: bool
    retention_policy: str


class ZkProofMetadataResponse(BaseModel):
    zk_ready: bool
    proof_type: str
    proof_status: str
    statement: str


class VerifyResponse(BaseModel):
    request_id: str
    correlation_id: str
    decision: Literal["allow", "deny"]
    cred_score: float
    age_check: AgeCheckResponse
    liveness_check: LivenessCheckResponse
    privacy: PrivacyMetadataResponse
    zk_proof: ZkProofMetadataResponse
    reason: Optional[str] = None
    raw: Optional[dict[str, Any]] = Field(default=None, exclude=True)
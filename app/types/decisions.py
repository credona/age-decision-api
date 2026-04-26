from typing import Any, Literal, Optional, TypedDict

PublicDecision = Literal["allow", "deny"]
CheckStatus = Literal["passed", "failed", "unknown"]


class NormalizedCheck(TypedDict):
    status: CheckStatus
    decision: PublicDecision
    reason: Optional[str]


class AgeCheck(NormalizedCheck, total=False):
    estimated_age: Optional[float]
    confidence: Optional[float]
    is_adult: Optional[bool]
    cred_decision_score: float


class LivenessCheck(NormalizedCheck, total=False):
    confidence: Optional[float]
    is_real: Optional[bool]
    spoof_detected: Optional[bool]
    cred_antispoof_score: float


class PrivacyMetadata(TypedDict):
    image_stored: bool
    biometric_template_stored: bool
    raw_image_logged: bool
    downstream_raw_response_exposed: bool
    retention_policy: str


class ZkProofMetadata(TypedDict):
    zk_ready: bool
    proof_type: str
    proof_status: str
    statement: str


class VerifyResult(TypedDict, total=False):
    request_id: str
    correlation_id: str
    decision: PublicDecision
    cred_global_score: float
    cred_score: float
    age_check: AgeCheck
    liveness_check: LivenessCheck
    privacy: PrivacyMetadata
    zk_proof: ZkProofMetadata
    reason: Optional[str]
    raw: dict[str, Any]
from app.types import ZkProofMetadata


def build_zk_proof_metadata() -> ZkProofMetadata:
    """
    Build Zero-Knowledge readiness metadata.

    V1.1 does not generate a cryptographic proof yet.
    It exposes a stable contract so that a future ZK verifier can be added
    without changing the public response shape.
    """
    return {
        "zk_ready": True,
        "proof_type": "interactive_zero_knowledge_ready",
        "proof_status": "not_generated",
        "statement": "The API is ready to prove an age decision without exposing the raw image or estimated age.",
    }
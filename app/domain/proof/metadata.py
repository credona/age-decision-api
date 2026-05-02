def build_zk_proof_metadata() -> dict:
    """
    Build ZK-ready metadata.

    This does not generate a cryptographic proof.
    It only preserves a future-compatible response structure.
    """
    return {
        "zk_ready": True,
        "proof_type": "interactive_zero_knowledge_ready",
        "proof_status": "not_generated",
        "statement": "The API is ready to prove a threshold decision without exposing the raw image, estimated age, or raw model scores.",
    }

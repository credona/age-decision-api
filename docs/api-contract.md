<h1>Age Decision API Contract</h1>

This document describes the public response contract exposed by the API gateway.

<hr>

<h2>Request</h2>

```json
{
  "image_base64": "base64-encoded-image",
  "country": "FR",
  "age_threshold": 18,
  "age_margin": 2,
  "confidence_threshold": 0.8
}
```

<h3>Headers</h3>

```text
X-Request-ID
X-Correlation-ID
```

If no correlation identifier is provided, the API uses the request identifier as the correlation identifier.

<hr>

<h2>Response</h2>

```json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "decision": "allow",
  "cred_global_score": 0.8,
  "cred_score": 0.8,
  "age_check": {
    "status": "passed",
    "decision": "allow",
    "reason": null,
    "estimated_age": 76.0,
    "confidence": 0.8,
    "is_adult": true,
    "cred_decision_score": 0.8
  },
  "liveness_check": {
    "status": "passed",
    "decision": "allow",
    "reason": null,
    "confidence": 0.99,
    "is_real": true,
    "spoof_detected": false,
    "cred_antispoof_score": 0.99
  },
  "privacy": {
    "image_stored": false,
    "biometric_template_stored": false,
    "raw_image_logged": false,
    "downstream_raw_response_exposed": false,
    "retention_policy": "not_stored_by_api_gateway"
  },
  "zk_proof": {
    "zk_ready": true,
    "proof_type": "interactive_zero_knowledge_ready",
    "proof_status": "not_generated",
    "statement": "The API is ready to prove an age decision without exposing the raw image or estimated age."
  },
  "reason": null
}
```

<hr>

<h2>Decision values</h2>

```text
allow
deny
```

The public decision is `allow` only when both normalized checks allow the request.

<hr>

<h2>Age check</h2>

The age check is normalized from the Core service.

It contains:

- `status`
- `decision`
- `reason`
- `estimated_age`
- `confidence`
- `is_adult`
- `cred_decision_score`

<hr>

<h2>Liveness check</h2>

The liveness check is normalized from the AntiSpoof service.

It contains:

- `status`
- `decision`
- `reason`
- `confidence`
- `is_real`
- `spoof_detected`
- `cred_antispoof_score`

<hr>

<h2>Credona score fields</h2>

<h3>cred_decision_score</h3>

Score produced by the Core service for the age decision.

<h3>cred_antispoof_score</h3>

Score produced by the AntiSpoof service for presentation attack detection.

<h3>cred_global_score</h3>

Final API-level score.

It is computed conservatively as the minimum of:

```text
cred_decision_score
cred_antispoof_score
```

<h3>cred_score</h3>

Temporary compatibility alias for `cred_global_score`.

New integrations should read `cred_global_score`.

<hr>

<h2>Error response</h2>

```json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "error": {
    "code": "invalid_base64_image",
    "message": "Invalid request."
  }
}
```

The API does not expose internal exception details.

<hr>

<h2>Privacy contract</h2>

The API gateway:

- does not store uploaded images
- does not store biometric templates
- does not log raw image content
- does not expose downstream raw responses by default
- orchestrates downstream calls in memory

<hr>

<h2>Zero-Knowledge readiness</h2>

`zk_proof` is a proof-ready metadata object.

It does not contain a cryptographic proof yet.

It exists to preserve a future-compatible response structure.

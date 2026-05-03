<h1>Age Decision API Contract</h1>

This document describes the public response contract exposed by the API gateway.

For ecosystem-wide compatibility policy, see:
https://github.com/credona/age-decision/blob/main/COMPATIBILITY.md

<hr>

<h2>Request</h2>

```json
{
  "image_base64": "base64-encoded-image",
  "majority_country": "FR",
  "age_threshold": 18
}
```

<h3>Headers</h3>

```text
X-Request-ID
X-Correlation-ID
```

If no correlation identifier is provided, the API uses the request identifier as the correlation identifier.

<hr>

<h2>Gateway responsibility</h2>

The API gateway orchestrates downstream services.

It does not perform model inference locally.

It does not load, download, store, or redistribute model binaries.

Model lifecycle and inference are delegated to:

- `age-decision-core`
- `age-decision-antispoof`

<hr>

<h2>Gateway metadata endpoints</h2>

The API exposes metadata endpoints for operational and compatibility checks:

```text
GET /health
GET /version
GET /ready
```

`/health` confirms that the API process is running.

`/version` exposes project metadata from `project.json`.

`/ready` checks downstream Core and AntiSpoof availability.

<hr>

<h2>Response</h2>

```json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "decision": "allow",
  "cred_global_score": 0.8,
  "decision_check": {
    "status": "passed",
    "decision": "allow",
    "reason": null,
    "threshold": {
      "type": "minimum_age",
      "value": 18,
      "source": "majority_country",
      "majority_country": "FR"
    },
    "cred_decision_score": 0.8
  },
  "spoof_check": {
    "status": "passed",
    "decision": "allow",
    "reason": null,
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
    "statement": "The API is ready to prove a threshold decision without exposing the raw image, estimated age, or raw model scores."
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
- `threshold`
- `cred_decision_score`

It does not contain:

- estimated age
- raw confidence
- `is_adult`

<hr>

<h2>Liveness check</h2>

The liveness check is normalized from the AntiSpoof service.

It contains:

- `status`
- `decision`
- `reason`
- `is_real`
- `spoof_detected`
- `cred_antispoof_score`

It does not contain:

- raw confidence
- spoof score
- internal threshold
- model details

<hr>

<h2>Credona score fields</h2>

<h3>cred_decision_score</h3>

Score produced by the Core service for the age threshold decision.

<h3>cred_antispoof_score</h3>

Score produced by the AntiSpoof service for presentation attack detection.

<h3>cred_global_score</h3>

Final API-level score.

It is computed conservatively as the minimum of:

```text
cred_decision_score
cred_antispoof_score
```

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

Version 2.3.0 contract governance additionally asserts:

- stable status contracts on <code>GET /health</code> and <code>GET /ready</code>
- standardized public <code>ErrorResponse</code> for normalized <code>POST /verify</code> validation and domain rejections (<code>invalid_base64_image</code>, <code>missing_image_base64</code>, <code>invalid_request</code>)
- downstream orchestration failures continue to normalize as <code>downstream_service_error</code> (HTTP 502) with stable messaging
- forbidden public leakage rules remain unchanged (<code>estimated_age</code>, raw confidences and scores, downstream raw payloads, legacy <code>cred_score</code>, stack traces)

<hr>

<h2>Privacy contract</h2>

The API gateway:

- does not store uploaded images
- does not store biometric templates
- does not log raw image content
- does not expose downstream raw responses by default
- does not expose estimated age
- does not expose raw model confidence
- does not expose raw anti-spoof model details
- does not load model binaries
- does not redistribute model binaries
- orchestrates downstream calls in memory

<hr>

<h2>Zero-Knowledge readiness</h2>

`zk_proof` is a proof-ready metadata object.

It does not contain a cryptographic proof yet.

It exists to preserve a future-compatible response structure.

<hr>

<h2>Project metadata</h2>

Project metadata is stored in:

```text
project.json
```

Generated view:

<!-- BEGIN:VERSION_RESPONSE -->
```json
{
  "service_name": "age-decision-api",
  "app_name": "Age Decision API",
  "version": "2.6.0",
  "contract_version": "2.6",
  "repository": "https://github.com/credona/age-decision-api",
  "image": "ghcr.io/credona/age-decision-api"
}
```
<!-- END:VERSION_RESPONSE -->

<hr>

<h2>Compatibility metadata</h2>

Compatibility metadata is stored in:

```text
compatibility.json
```

Generated view:

<!-- BEGIN:COMPATIBILITY_METADATA -->
```json
{
  "service": "age-decision-api",
  "version": "2.6.0",
  "contract_version": "2.6",
  "compatible_with": {
    "age-decision-core": ">=2.0.0 <3.0.0",
    "age-decision-antispoof": ">=2.0.0 <3.0.0",
    "age-decision-js": ">=2.0.0 <3.0.0"
  },
  "public_contract": {
    "decision_values": [
      "allow",
      "deny"
    ],
    "score_field": "cred_global_score",
    "internal_estimate_exposed": false,
    "raw_decision_signal_quality_exposed": false,
    "raw_spoof_signal_quality_exposed": false,
    "downstream_raw_response_exposed_by_default": false,
    "legacy_cred_score_exposed": false
  }
}
```
<!-- END:COMPATIBILITY_METADATA -->

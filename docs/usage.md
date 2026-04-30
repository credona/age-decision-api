<h1>Age Decision API Usage</h1>

This document describes how to run and call the public Age Decision API gateway.

<hr>

<h2>Contributor usage</h2>

Start the full development stack:

~~~bash
./scripts/docker/dev.sh
~~~

Stop the stack:

~~~bash
docker compose --env-file .generated/compose/dev.env -f docker-compose.dev.yml down
~~~

View API logs:

~~~bash
docker compose --env-file .generated/compose/dev.env -f docker-compose.dev.yml logs -f age-decision-api
~~~

<hr>

<h2>Runtime dependencies</h2>

The API gateway depends on downstream services:

~~~text
age-decision-core
age-decision-antispoof
~~~

It does not run local model inference.

It does not download or load model files.

Model lifecycle is owned by downstream services.

<hr>

<h2>Runtime configuration</h2>

Default runtime values are declared in:

~~~text
project.json
~~~

Generated runtime files are written to:

~~~text
.generated/runtime/
~~~

Generated Compose files are written to:

~~~text
.generated/compose/
~~~

Do not edit generated files manually.

Regenerate them with:

~~~bash
./scripts/config/generate_env.sh dev
~~~

<hr>

<h2>Health checks</h2>

~~~bash
curl -i http://localhost:8002/health
curl -i http://localhost:8002/version
curl -i http://localhost:8002/ready
~~~

Expected health response:

<!-- BEGIN:HEALTH_RESPONSE -->
```json
{
  "status": "ok",
  "service": "age-decision-api",
  "version": "2.2.3",
  "contract_version": "2.2"
}
```
<!-- END:HEALTH_RESPONSE -->

Expected version response:

<!-- BEGIN:VERSION_RESPONSE -->
```json
{
  "service_name": "age-decision-api",
  "app_name": "Age Decision API",
  "version": "2.2.3",
  "contract_version": "2.2",
  "repository": "https://github.com/credona/age-decision-api",
  "image": "ghcr.io/credona/age-decision-api"
}
```
<!-- END:VERSION_RESPONSE -->

Expected readiness response:

<!-- BEGIN:READY_RESPONSE -->
```json
{
  "status": "ready",
  "service": "age-decision-api",
  "version": "2.2.3",
  "contract_version": "2.2",
  "core": {
    "status": "ready",
    "url": "http://age-decision-core:8000"
  },
  "antispoof": {
    "status": "ready",
    "url": "http://age-decision-antispoof:8001"
  }
}
```
<!-- END:READY_RESPONSE -->

<hr>

<h2>Verify</h2>

~~~bash
IMAGE_BASE64=$(base64 -w 0 test-face.jpg)

curl -X POST http://localhost:8002/verify \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-001" \
  -H "X-Correlation-ID: test-correlation-001" \
  -d "{\"image_base64\":\"$IMAGE_BASE64\",\"majority_country\":\"FR\",\"age_threshold\":18}"
~~~

Example response:

~~~json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "decision": "allow",
  "cred_global_score": 0.8,
  "age_check": {
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
  "liveness_check": {
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
~~~

<hr>

<h2>External Docker usage</h2>

Run from the published image:

~~~bash
docker run --rm \
  -p 8002:8000 \
  -e AGE_DECISION_CORE_URL=http://age-decision-core:8000 \
  -e AGE_DECISION_ANTISPOOF_URL=http://age-decision-antispoof:8001 \
  ghcr.io/credona/age-decision-api:latest
~~~

<hr>

<h2>Public privacy contract</h2>

The public `/verify` response does not expose:

- estimated age
- raw age confidence
- `is_adult`
- raw liveness confidence
- spoof score
- downstream model details
- legacy `cred_score` alias

<hr>

<h2>Error response</h2>

Error responses follow a stable JSON format.

The API does not expose internal exception details.

~~~json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "error": {
    "code": "invalid_base64_image",
    "message": "Invalid request."
  }
}
~~~

Known error codes:

~~~text
invalid_base64_image
downstream_service_error
~~~

The `message` field is intentionally generic and stable.

Detailed error context is available only in server logs.

<hr>

<h2>Validation</h2>

Run the full auto-fix and validation pipeline:

~~~bash
./scripts/ci/fix_all_docker.sh
~~~

Run validation only:

~~~bash
./scripts/ci/check_all_docker.sh
~~~

<hr>

<h2>Compatibility metadata</h2>

<!-- BEGIN:COMPATIBILITY_METADATA -->
```json
{
  "service": "age-decision-api",
  "version": "2.2.3",
  "contract_version": "2.2",
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
    "estimated_age_exposed": false,
    "raw_age_confidence_exposed": false,
    "raw_liveness_confidence_exposed": false,
    "downstream_raw_response_exposed_by_default": false,
    "legacy_cred_score_exposed": false
  }
}
```
<!-- END:COMPATIBILITY_METADATA -->

<h1>Age Decision API Usage</h1>

This document describes how to run and call the public Age Decision API gateway.

For global concepts, architecture and roadmap, see:

```text
https://github.com/credona/age-decision
```

<hr>

<h2>Environment</h2>

Create a local environment file:

```bash
cp .env.example.dev .env
```

Example:

```env
APP_ENV=development
APP_PORT=8002

AGE_DECISION_CORE_URL=http://age-decision-core:8000
AGE_DECISION_ANTISPOOF_URL=http://age-decision-antispoof:8001

REQUEST_TIMEOUT=3000
LOG_LEVEL=info

EXPOSE_RAW_DOWNSTREAM_RESPONSES=false
```

Project identity metadata is stored in:

```text
project.json
```

Runtime environment files must not override:

```text
service_name
app_name
version
contract_version
```

<hr>

<h2>Runtime dependencies</h2>

The API gateway depends on downstream services:

```text
age-decision-core
age-decision-antispoof
```

It does not run local model inference.

It does not download or load model files.

Model lifecycle is owned by the downstream services.

<hr>

<h2>Run local stack</h2>

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

View logs:

```bash
docker compose -f docker-compose.dev.yml logs -f age-decision-api
```

Stop services:

```bash
docker compose -f docker-compose.dev.yml down -v
```

<hr>

<h2>Health</h2>

```bash
curl -i http://localhost:8002/health
```

Example response:

<!-- BEGIN:HEALTH_RESPONSE -->
```json
{}
```
<!-- END:HEALTH_RESPONSE -->

<hr>

<h2>Version</h2>

```bash
curl -i http://localhost:8002/version
```

Example response:

<!-- BEGIN:VERSION_RESPONSE -->
```json
{}
```
<!-- END:VERSION_RESPONSE -->

<hr>

<h2>Readiness</h2>

```bash
curl -i http://localhost:8002/ready
```

Example response:

<!-- BEGIN:READY_RESPONSE -->
```json
{}
```
<!-- END:READY_RESPONSE -->

<hr>

<h2>Verify</h2>

```bash
IMAGE_BASE64=$(base64 -w 0 test-face.jpg)

curl -X POST http://localhost:8002/verify \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-001" \
  -H "X-Correlation-ID: test-correlation-001" \
  -d "{\"image_base64\":\"$IMAGE_BASE64\",\"majority_country\":\"FR\",\"age_threshold\":18}"
```

Example response:

```json
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
```

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

Known error codes:

```text
invalid_base64_image
downstream_service_error
```

The `message` field is intentionally generic and stable.

Detailed error context is available only in server logs.

<hr>

<h2>Compatibility metadata</h2>

Compatibility metadata is declared in:

```text
compatibility.json
```

Generated view:

<!-- BEGIN:COMPATIBILITY_METADATA -->
```json
{}
```
<!-- END:COMPATIBILITY_METADATA -->

<hr>

<h2>Tests</h2>

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

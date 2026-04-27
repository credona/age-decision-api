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
APP_NAME=age-decision-api
APP_ENV=development
APP_PORT=8002

AGE_DECISION_CORE_URL=http://age-decision-core:8000
AGE_DECISION_ANTISPOOF_URL=http://age-decision-antispoof:8001

REQUEST_TIMEOUT=3000
LOG_LEVEL=info

EXPOSE_RAW_DOWNSTREAM_RESPONSES=false
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

```json
{
  "status": "ok",
  "service": "age-decision-api"
}
```

<hr>

<h2>Readiness</h2>

```bash
curl -i http://localhost:8002/ready
```

Example response:

```json
{
  "status": "ready",
  "service": "age-decision-api",
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

<hr>

<h2>Verify</h2>

```bash
IMAGE_BASE64=$(base64 -w 0 test-face.jpg)

curl -X POST http://localhost:8002/verify \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-001" \
  -H "X-Correlation-ID: test-correlation-001" \
  -d "{\"image_base64\":\"$IMAGE_BASE64\",\"country\":\"FR\",\"age_threshold\":18}"
```

Example response:

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
    "estimated_age": 76.0,
    "confidence": 0.8,
    "is_adult": true,
    "cred_decision_score": 0.8
  },
  "liveness_check": {
    "status": "passed",
    "decision": "allow",
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

<h2>Tests</h2>

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

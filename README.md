<h1>Age Decision API</h1>

Age Decision API is the public gateway of the Age Decision system.

It orchestrates age estimation and anti-spoofing services to produce a unified, privacy-first decision.

---

<h2>Overview</h2>

The API exposes a single verification endpoint that:

- accepts a base64-encoded image
- calls `age-decision-core` (age estimation)
- calls `age-decision-antispoof` (anti-spoofing)
- aggregates results into a single decision
- computes a global `cred_score`
- returns privacy metadata
- exposes a ZK-ready contract

---

<h2>Architecture</h2>

```text
Client
  ↓
age-decision-api
  ├── age-decision-core (/estimate)
  └── age-decision-antispoof (/check)
```

---

<h2>Features</h2>

- Unified decision: `allow / deny`
- Credona scoring system (`cred_score`)
- Structured JSON logs
- Request tracing:
  - `X-Request-ID`
  - `X-Correlation-ID`
- Privacy-first design
- Zero-Knowledge ready contract
- Health and readiness endpoints
- Local Docker development setup

---

<h2>Status</h2>

Current version: <b>v1.0.0</b>

Test status:

```text
17 passed
```

---

<h2>Configuration</h2>

```bash
cp .env.example .env
```

```env
APP_NAME=age-decision-api
APP_ENV=development
APP_PORT=8002
API_VERSION=1.0.0

AGE_DECISION_CORE_URL=http://age-decision-core:8000
AGE_DECISION_ANTISPOOF_URL=http://age-decision-antispoof:8001

REQUEST_TIMEOUT=3000
LOG_LEVEL=info

EXPOSE_RAW_DOWNSTREAM_RESPONSES=false
```

---

<h2>Local Development with Docker</h2>

The Docker configuration in this repository is intended for local development only.

It does not represent the production deployment configuration of Credona hosted services.

```bash
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

---

<h2>API Endpoints</h2>

<h3>Health</h3>

```bash
GET /health
```

```json
{
  "status": "ok",
  "service": "age-decision-api"
}
```

---

<h3>Readiness</h3>

```bash
GET /ready
```

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

---

<h3>Verify</h3>

```bash
POST /verify
Content-Type: application/json
```

<h4>Request</h4>

```json
{
  "image_base64": "base64-encoded-image",
  "country": "FR",
  "age_threshold": 18
}
```

<h4>Example</h4>

```bash
IMAGE_BASE64=$(base64 -w 0 test-face.jpg)

curl -X POST http://localhost:8002/verify \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-001" \
  -H "X-Correlation-ID: test-correlation-001" \
  -d "{\"image_base64\":\"$IMAGE_BASE64\",\"country\":\"FR\",\"age_threshold\":18}"
```

<h4>Response</h4>

```json
{
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "decision": "allow",
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

---

<h2>Cred Score</h2>

The `cred_score` represents the reliability of the decision.

- Range: `0.0 → 1.0`
- Computed as the minimum of:
  - `cred_decision_score`
  - `cred_antispoof_score`

---

<h2>Privacy</h2>

- No image storage
- No biometric template storage
- No raw image logging
- No persistent data at API level

---

<h2>Zero-Knowledge Ready</h2>

- No raw image exposure required
- Decision can be proven without revealing age
- Future support for cryptographic proof generation

---

<h2>Testing</h2>

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

Expected:

```text
17 passed
```

---

<h2>Logs</h2>

```json
{
  "timestamp": "2026-04-25T20:00:00Z",
  "level": "INFO",
  "event": "verification_completed",
  "request_id": "test-request-001",
  "correlation_id": "test-correlation-001",
  "data": {
    "decision": "allow",
    "cred_score": 0.8
  }
}
```

---

<h2>Scope</h2>

This service:

- orchestrates age and anti-spoofing decisions
- exposes a unified verification API
- provides a privacy-first response

It does not:

- perform identity verification
- store images
- generate real Zero Knowledge proofs in v1.0.0

---

<h2>Roadmap</h2>

See `ROADMAP.md`.

---

<h2>License</h2>

Apache License 2.0
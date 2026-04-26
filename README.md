<h1>Age Decision API</h1>

<p>
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/ci.yml?branch=main&label=CI" alt="CI">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/docker.yml?branch=main&label=Docker" alt="Docker">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/codeql.yml?branch=main&label=CodeQL" alt="CodeQL">
  <img src="https://img.shields.io/github/v/release/credona/age-decision-api" alt="Release">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="License">
</p>

Age Decision API is the public gateway of the Age Decision system.

It orchestrates age estimation and anti-spoofing services to produce a unified, privacy-first decision.

<hr>

<h2>Overview</h2>

The API exposes a single verification endpoint that:

- accepts a base64-encoded image
- calls `age-decision-core` for age estimation
- calls `age-decision-antispoof` for anti-spoofing
- aggregates results into a single decision
- computes a global `cred_score`
- returns privacy metadata
- exposes a ZK-ready contract
- propagates `request_id` and `correlation_id`

<hr>

<h2>Architecture</h2>

```text
Client
  ↓
age-decision-api
  ├── age-decision-core (/estimate)
  └── age-decision-antispoof (/check)
```

<hr>

<h2>Features</h2>

- Unified decision: `allow / deny`
- Credona scoring system: `cred_score`
- Core decision score: `cred_decision_score`
- Anti-spoof score: `cred_antispoof_score`
- Structured JSON logs
- Request tracing:
  - `X-Request-ID`
  - `X-Correlation-ID`
- Privacy-first response metadata
- Zero-Knowledge ready contract
- Health and readiness endpoints
- Local Docker development setup
- Docker image distribution through GHCR
- GitHub Actions CI, Docker, CodeQL and release workflows

<hr>

<h2>Status</h2>

Current version: <b>v1.1.0</b>

Validated status:

```text
17 passed
```

<hr>

<h2>Repository structure</h2>

```text
age-decision-api/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── codeql.yml
│   │   ├── docker.yml
│   │   └── release.yml
│   └── dependabot.yml
├── app/
│   ├── api/
│   ├── clients/
│   ├── config/
│   ├── models/
│   ├── normalizers/
│   ├── services/
│   ├── types/
│   ├── logging_config.py
│   ├── main.py
│   ├── privacy.py
│   ├── version.py
│   └── zk.py
├── scripts/
├── tests/
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── ROADMAP.md
├── LICENSE
└── README.md
```

<hr>

<h2>Environment variables</h2>

Example `.env` for local development:

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

`API_VERSION` is defined in `app/version.py`.

It is not required in the runtime environment.

<hr>

<h2>Local Development with Docker</h2>

The Docker configuration in this repository is intended for local development only.

It does not represent the production deployment configuration of Credona hosted services.

Start the full local stack from source:

```bash
cp .env.example.dev .env
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

Run tests:

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
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

<h2>Docker image</h2>

The production-oriented image is built from `Dockerfile`.

Build locally:

```bash
docker build -t age-decision-api:local .
```

Run locally:

```bash
docker run --rm -p 8002:8000 age-decision-api:local
```

Official GHCR image:

```text
ghcr.io/credona/age-decision-api
```

Available tags after release:

```text
ghcr.io/credona/age-decision-api:v1.0.1
ghcr.io/credona/age-decision-api:v1.0.2
ghcr.io/credona/age-decision-api:v1.0.3
ghcr.io/credona/age-decision-api:v1.1.0
ghcr.io/credona/age-decision-api:latest
```

Run the image-based stack:

```bash
cp .env.example.dev .env
docker compose down -v
docker compose up -d
```

<hr>

<h2>API endpoints</h2>

<h3>Health</h3>

```bash
curl -i http://localhost:8002/health
```

```json
{
  "status": "ok",
  "service": "age-decision-api"
}
```

<h3>Readiness</h3>

```bash
curl -i http://localhost:8002/ready
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

<hr>

<h2>Cred Score</h2>

The `cred_score` represents the reliability of the final decision.

- Range: `0.0 -> 1.0`
- Computed as the minimum of:
  - `cred_decision_score`
  - `cred_antispoof_score`

A low score means that at least one required signal is weak.

<hr>

<h2>Privacy</h2>

The API gateway does not persist uploaded images.

It does not store biometric templates, log raw images, or expose downstream raw responses unless explicitly configured.

Default behavior:

- no image storage
- no biometric template storage
- no raw image logging
- no persistent data at API level
- in-memory orchestration only

<hr>

<h2>Zero-Knowledge Ready</h2>

The current version exposes a proof-friendly response contract.

It does not generate a real cryptographic Zero-Knowledge proof in `v1.1.0`.

The goal is to prepare future verification flows where a decision can be proven without exposing:

- the raw image
- the estimated age
- the downstream service internals

<hr>

<h2>Logging</h2>

Logs are structured JSON events.

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

<hr>

<h2>Automation</h2>

This repository includes:

- GitHub Actions CI
- automated tests on pull requests
- Docker image build
- automated GHCR publishing
- automated GitHub release creation
- tag-based release notes
- CodeQL scanning
- Dependabot updates

<hr>

<h2>Testing</h2>

Run all tests:

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

Current result:

```text
17 passed
```

<hr>

<h2>Scope</h2>

This service:

- orchestrates age and anti-spoofing decisions
- exposes a unified verification API
- computes a global Credona score
- provides a privacy-first response
- exposes a ZK-ready contract

It does not:

- perform identity verification
- store images
- generate real Zero-Knowledge proofs in `v1.1.0`
- replace certified legal identity checks
- perform face recognition

<hr>

<h2>Integration with Age Decision</h2>

`age-decision-core` handles face detection and age estimation.

`age-decision-antispoof` handles real / spoof analysis.

`age-decision-api` orchestrates both services and exposes the final verification API.

```text
image
→ age-decision-api
  → age-decision-core
  → age-decision-antispoof
→ final decision
```

<hr>

<h2>Roadmap</h2>

See `ROADMAP.md`.

<hr>

<h2>License</h2>

This repository is released under the Apache License 2.0.

See the `LICENSE` file for details.

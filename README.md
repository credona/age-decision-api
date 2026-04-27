<h1>Age Decision API</h1>

<p>
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/ci.yml?branch=main&label=CI" alt="CI">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/docker.yml?branch=main&label=Docker" alt="Docker">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/codeql.yml?branch=main&label=CodeQL" alt="CodeQL">
  <img src="https://img.shields.io/github/v/release/credona/age-decision-api" alt="Release">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="License">
</p>

Age Decision API is the public gateway of the Age Decision ecosystem.

It orchestrates threshold age decision and anti-spoofing services to produce a unified, privacy-first verification decision.

It does not perform model inference locally.

It does not load, store, download, or redistribute machine learning model binaries.

<hr>

<h2>Documentation</h2>

- Usage: docs/usage.md
- API contract: docs/api-contract.md
- Changelog: CHANGELOG.md
- Contributing: CONTRIBUTING.md
- Global project: https://github.com/credona/age-decision

<hr>

<h2>Service role</h2>

```text
Client
  → age-decision-api
    → age-decision-core
    → age-decision-antispoof
  → unified verification response
```

The API gateway is responsible for:

- base64 request handling
- downstream orchestration
- request tracing
- response normalization
- global decision aggregation
- global Credona score computation
- privacy metadata exposure
- ZK-ready metadata exposure

The API gateway is not responsible for:

- direct age model inference
- direct anti-spoof model inference
- model file management
- model download
- model redistribution

<hr>

<h2>Quickstart</h2>

```bash
cp .env.example.dev .env
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

Check the service:

```bash
curl -i http://localhost:8002/health
curl -i http://localhost:8002/ready
```

Run tests:

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

<hr>

<h2>Docker image</h2>

```text
ghcr.io/credona/age-decision-api
```

The API image contains only the gateway runtime.

It should not contain ONNX, PyTorch, TensorFlow, or other model binaries.

<hr>

<h2>Public endpoint</h2>

```text
POST /verify
```

The endpoint accepts a base64 image and returns:

- `decision`
- `cred_global_score`
- `age_check`
- `liveness_check`
- `privacy`
- `zk_proof`
- `request_id`
- `correlation_id`

The public response does not expose:

- estimated age
- raw age confidence
- `is_adult`
- raw liveness confidence
- spoof score
- downstream model details
- legacy `cred_score` alias

<hr>

<h2>Scope</h2>

This service does not:

- perform local age estimation
- perform local anti-spoofing
- perform identity verification
- store images
- store biometric templates
- download model files
- redistribute model files
- generate real Zero-Knowledge proofs
- replace certified legal identity checks
- perform face recognition

<hr>

<h2>License</h2>

This repository is released under the Apache License 2.0.

See LICENSE for details.

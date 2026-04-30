<h1>Age Decision API</h1>

<p>
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/ci.yml?branch=main&label=CI" alt="CI">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/docker.yml?branch=main&label=Docker" alt="Docker">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/codeql.yml?branch=main&label=CodeQL" alt="CodeQL">
  <img src="https://img.shields.io/github/v/release/credona/age-decision-api" alt="Release">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="License">
</p>

Age Decision API is the public gateway of the Age Decision ecosystem.

It orchestrates downstream services and exposes a unified, privacy-first verification decision.

It does not perform model inference locally.

It does not load, store, download, or redistribute machine learning model binaries.

<hr>

<h2>Documentation</h2>

- Repository: https://github.com/credona/age-decision-api
- Usage: docs/usage.md
- API contract: docs/api-contract.md
- Compatibility: docs/compatibility.md
- Changelog: CHANGELOG.md
- Contributing: CONTRIBUTING.md
- Global project: https://github.com/credona/age-decision

<hr>

<h2>Quickstart for contributors</h2>

Start the full development stack:

~~~bash
./scripts/docker/dev.sh
~~~

Check the gateway:

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
  "version": "2.2.2",
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
  "version": "2.2.2",
  "contract_version": "2.2",
  "repository": "https://github.com/credona/age-decision-api",
  "image": "ghcr.io/credona/age-decision-api"
}
```
<!-- END:VERSION_RESPONSE -->

<hr>

<h2>One-command workflow</h2>

Auto-fix, regenerate metadata and documentation, then validate everything:

~~~bash
./scripts/ci/fix_all_docker.sh
~~~

Run strict validation only:

~~~bash
./scripts/ci/check_all_docker.sh
~~~

Start the development stack:

~~~bash
./scripts/docker/dev.sh
~~~

Build the API image with metadata from `project.json`:

~~~bash
./scripts/docker/build.sh prod
./scripts/docker/build.sh dev
~~~

<hr>

<h2>Configuration model</h2>

Project metadata and default runtime values are declared once in:

~~~text
project.json
~~~

Generated environment files are created under:

~~~text
.generated/
~~~

Do not edit generated files manually.

The repository does not use committed `.env` files.

External users may still override runtime values with Docker environment variables.

Example:

~~~bash
docker run --rm \
  -p 8002:8000 \
  -e AGE_DECISION_CORE_URL=http://age-decision-core:8000 \
  -e AGE_DECISION_ANTISPOOF_URL=http://age-decision-antispoof:8001 \
  ghcr.io/credona/age-decision-api:latest
~~~

<hr>

<h2>Service role</h2>

~~~text
Client
  -> age-decision-api
    -> age-decision-core
    -> age-decision-antispoof
  -> unified verification response
~~~

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

<h2>Public endpoint</h2>

~~~text
POST /verify
~~~

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

<h2>Compatibility metadata</h2>

Compatibility metadata is declared in `compatibility.json` and synchronized from `project.json`.

<!-- BEGIN:COMPATIBILITY_METADATA -->
```json
{
  "service": "age-decision-api",
  "version": "2.2.2",
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

<hr>

<h2>Docker image</h2>

~~~text
ghcr.io/credona/age-decision-api
~~~

The API image contains only the gateway runtime.

It should not contain ONNX, PyTorch, TensorFlow, or other model binaries.

<hr>

<h2>License</h2>

This repository is released under the Apache License 2.0.

See LICENSE for details.

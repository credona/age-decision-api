<h1>Age Decision API</h1>

<p>
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/ci.yml?branch=main&label=CI" alt="CI">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/docker.yml?branch=main&label=Docker" alt="Docker">
  <img src="https://img.shields.io/github/actions/workflow/status/credona/age-decision-api/codeql.yml?branch=main&label=CodeQL" alt="CodeQL">
  <img src="https://img.shields.io/github/v/release/credona/age-decision-api" alt="Release">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="License">
</p>

Age Decision API is the public gateway of the Age Decision ecosystem.

<h2>Responsibility</h2>

This repository owns public request handling, downstream orchestration, and global decision aggregation.

<h2>Scope</h2>

It orchestrates downstream services and exposes a unified, privacy-first verification decision.

It does not perform model inference locally.

It does not load, store, download, or redistribute machine learning model binaries.

Version 2.3.0 documents public gateway contract governance: stable <code>/health</code> and <code>/ready</code> regression coverage, standardized error envelopes, normalized <code>/verify</code> JSON validation (including <code>missing_image_base64</code>), preserved downstream failure normalization, and unchanged privacy-first field rules.

<hr>

<h2>When to use this repository</h2>

- you want a unified verification endpoint
- you want orchestration between core and antispoof
- you need a production-ready entry point

<h2>When NOT to use this repository</h2>

- you want raw model access
- you want to run inference locally
- you want direct control over scoring internals

<hr>

<h2>Documentation</h2>

- Repository: https://github.com/credona/age-decision-api
- Usage: docs/usage.md
- API contract: docs/api-contract.md
- Compatibility: docs/compatibility.md
- Security: SECURITY.md
- Global architecture and ownership: https://github.com/credona/age-decision/blob/main/docs/architecture.md
- Global scoring model: https://github.com/credona/age-decision/blob/main/docs/scoring.md
- Changelog: CHANGELOG.md
- Contributing: CONTRIBUTING.md
- Global project: https://github.com/credona/age-decision

<hr>

<h2>Usage example</h2>

Call the public verification endpoint:

~~~bash
curl -X POST "http://localhost:8002/verify" \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: test-request-001" \
  -H "X-Correlation-ID: test-correlation-001" \
  -d '{"image_base64":"base64-image","majority_country":"FR","age_threshold":18}'
~~~

<hr>

For setup, runtime configuration, contributor workflows, and full API response details, see `docs/usage.md`.

<hr>

<h2>License</h2>

This repository is released under the Apache License 2.0.

See LICENSE for details.

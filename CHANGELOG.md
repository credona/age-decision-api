<h1>Changelog</h1>

This changelog tracks changes specific to Age Decision API.

Global project direction is tracked in the central Age Decision repository.

<hr>

<h2>2.0.0</h2>

- Introduced privacy-first public verification contract.
- Aligned API response with Core 2.0.0 threshold decision contract.
- Aligned API response with AntiSpoof 2.0.0 public contract.
- Replaced `country` request field with `majority_country`.
- Removed `age_margin` and `confidence_threshold` from the public request contract.
- Removed `estimated_age` from public verification responses.
- Removed raw age confidence from public verification responses.
- Removed `is_adult` from public verification responses.
- Removed liveness raw confidence from public verification responses.
- Removed legacy `cred_score` compatibility alias from public verification responses.
- Kept `cred_global_score` as the only global Credona score.
- Kept `cred_decision_score` as the normalized Core score.
- Kept `cred_antispoof_score` as the normalized AntiSpoof score.
- Updated downstream normalization for `match`, `no_match`, and `uncertain` Core decisions.
- Updated downstream normalization for privacy-first AntiSpoof responses.
- Updated public documentation and contract tests.

<hr>

<h2>1.2.1</h2>

- Documentation structure simplified.
- Repository README reduced to a concise entry point.
- Usage moved to docs/usage.md.
- Public API contract moved to docs/api-contract.md.
- Local roadmap removed in favor of the central roadmap.

<hr>

<h2>1.2.0</h2>

- Renamed final `cred_score` to `cred_global_score`.
- Kept `cred_score` as a temporary compatibility alias.
- Consumed `cred_decision_score` from Core.
- Consumed `cred_antispoof_score` from AntiSpoof.
- Added stable error response schema.
- Added request tracing to error responses.
- Added OpenAPI contract tests.
- Updated response documentation.

<hr>

<h2>1.1.0</h2>

- Upgraded API Docker runtime to Python 3.14.
- Validated API runtime compatibility.
- Validated downstream service compatibility.
- Validated health endpoint.
- Validated readiness endpoint.
- Validated verification endpoint with real image.

<hr>

<h2>1.0.3</h2>

- Updated GitHub Actions workflow dependencies.
- Validated CI workflow execution.
- Validated Docker build workflow.
- Validated release workflow.

<hr>

<h2>1.0.2</h2>

- Updated Python dependencies.
- Validated Docker runtime after dependency updates.
- Validated health endpoint.
- Validated readiness endpoint.
- Validated verification endpoint with real image.

<hr>

<h2>1.0.1</h2>

- Added CI workflow.
- Added Docker image workflow.
- Added release workflow.
- Added CodeQL scanning.
- Added Dependabot configuration.
- Added image-based docker-compose stack.
- Published Docker image through GHCR.

<hr>

<h2>1.0.0</h2>

- Initial public release.
- Added base64 verification endpoint.
- Added Core and AntiSpoof orchestration.
- Added global Credona score aggregation.
- Added privacy metadata.
- Added ZK-ready contract.
- Added structured logging.
- Added request tracing.
- Added health and readiness endpoints.
- Added local Docker development setup.

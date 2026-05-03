<h1>Changelog</h1>

This changelog tracks changes specific to Age Decision API.

Global project direction is tracked in the central Age Decision repository.

<h2>2.6.0</h2>

<ul>
  <li>Added privacy-safe benchmark report schema for API end-to-end benchmarks.</li>
  <li>Added API end-to-end benchmark execution script for the public verification flow.</li>
  <li>Added aggregate latency, decision distribution, and spoof-check presence metrics.</li>
  <li>Added machine, runtime, dataset, and hosting provider metadata in benchmark reports.</li>
  <li>Added benchmark privacy tests preventing raw payloads and downstream response exposure.</li>
  <li>Added benchmark output schema tests for reproducible reporting.</li>
  <li>Validated the release through Docker CI-equivalent checks.</li>
</ul>

<hr>

<h2>2.5.0</h2>

<ul>
  <li>Introduced strict client ports for Core and Antispoof services with full async contract.</li>
  <li>Decoupled VerificationOrchestrator from infrastructure using port-based injection.</li>
  <li>Enforced response_filter as final public contract boundary stripping internal payloads.</li>
  <li>Added architecture tests preventing direct infrastructure usage in application layer.</li>
  <li>Introduced a versioned global scoring policy for cred_global_score.</li>
  <li>Defined cred_global_score as a conservative minimum of public downstream scores.</li>
  <li>Removed raw downstream response exposure from the public verification flow.</li>
  <li>Simplified runtime configuration with shared common values and empty dev/prod overrides.</li>
  <li>Removed non-deterministic runtime flags and downstream model threshold settings.</li>
  <li>Added score bounds, monotonicity, stability, and privacy regression tests.</li>
  <li>Documented the public API scoring methodology.</li>
  <li>Preserved response_filter as the final public contract barrier.</li>
  <li>Preserved privacy-first orchestration without exposing downstream internals.</li>
  <li>Validated the release through Docker CI-equivalent checks.</li>
</ul>

<hr>

<h2>2.4.0</h2>

<ul>
  <li>Introduced hexagonal orchestration boundaries for API, application, domain, and infrastructure code.</li>
  <li>Added privacy-safe logging tests covering raw payloads, downstream responses, scores, thresholds, and base64 leakage.</li>
  <li>Added deterministic rejection for unsupported v3 input types before orchestration.</li>
  <li>Prepared the public request model for v3 multi-input support while only image remains supported in v2.4.0.</li>
  <li>Renamed verification use case to run verification terminology.</li>
  <li>Renamed age and liveness normalized outputs to decision check and spoof check.</li>
  <li>Renamed normalizers to decision and spoof normalizers.</li>
  <li>Centralized public decisions, statuses, error codes, proof metadata, privacy metadata, and readiness constants.</li>
  <li>Updated generated compatibility and usage documentation for neutral public terminology.</li>
  <li>Preserved privacy-first response filtering and forbidden field checks.</li>
  <li>Validated the refactor through Docker CI-equivalent checks.</li>
</ul>

<hr>

<h2>2.3.0</h2>

<ul>
  <li>Added stable public status contract regression coverage for <code>/health</code> and <code>/ready</code>.</li>
  <li>Standardized the public error response model to expose only <code>request_id</code>, <code>correlation_id</code>, and <code>error</code>.</li>
  <li>Normalized structured JSON validation failures on <code>POST /verify</code> to the same ErrorResponse envelope.</li>
  <li>Mapped missing <code>image_base64</code> validations to <code>missing_image_base64</code> with HTTP 400 and <code>Invalid request.</code>.</li>
  <li>Preserved downstream failure normalization (<code>downstream_service_error</code>) with stable messaging.</li>
  <li>Preserved privacy-first forbidden field guarantees for public gateway outputs.</li>
  <li>Documented public gateway deprecation rules in <code>docs/deprecation-policy.md</code>.</li>
  <li>Documented the gateway error model and known codes in <code>docs/error-model.md</code>.</li>
  <li>Documented stable status endpoints and <code>contract_version</code> behavior in <code>docs/status-contract.md</code>.</li>
</ul>

<hr>

<h2>2.2.3</h2>

<ul>
  <li>Enforced documentation boundaries between global and repository-specific docs.</li>
  <li>Removed cross-repository documentation duplication.</li>
  <li>Normalized repository <code>README.md</code> scope.</li>
  <li>Normalized <code>CONTRIBUTING.md</code> to local workflows.</li>
  <li>Normalized <code>SECURITY.md</code> and <code>COMPATIBILITY.md</code> scope.</li>
  <li>Enforced absolute GitHub links only for cross-repository documentation references.</li>
  <li>Centralized global documentation in <code>age-decision</code>.</li>
</ul>

<hr>

<h2>2.2.2</h2>

<ul>
  <li>Published Docker images from version tags only; pull request workflows no longer publish Docker images.</li>
  <li>Release workflow builds GitHub release description from the matching <code>CHANGELOG.md</code> section.</li>
  <li>Release workflow validates the Git tag matches <code>project.json</code> and that exactly one GHCR package version carries that tag.</li>
  <li>Added manual and scheduled workflow to delete untagged GHCR Docker package versions.</li>
</ul>

<hr>

<h2>2.2.1</h2>

<ul>
  <li>Introduced single source of truth configuration via project.json.</li>
  <li>Added dynamic environment generation for Docker (compose and runtime).</li>
  <li>Removed static .env usage in favor of generated configuration.</li>
  <li>Added Docker image metadata injection using build arguments.</li>
  <li>Added Docker metadata consistency validation.</li>
  <li>Added compatibility metadata auto-synchronization.</li>
  <li>Added automatic documentation synchronization checks.</li>
  <li>Added one-command auto-fix pipeline (fix_all_docker.sh).</li>
  <li>Added one-command CI-equivalent validation (check_all_docker.sh).</li>
  <li>Added Docker-first local CI execution.</li>
  <li>Added pre-push validation hook aligned with CI.</li>
  <li>Simplified API gateway developer workflow.</li>
</ul>

<hr>

<h2>2.2.0</h2>

<ul>
  <li>Added one-command local validation.</li>
  <li>Added one-command release preparation.</li>
  <li>Reorganized developer, CI, metadata, documentation, and release scripts.</li>
  <li>Added automatic release tagging from project metadata after main CI success.</li>
  <li>Aligned release and Docker workflows with tag-triggered automation.</li>
</ul>

<hr>

<h2>2.1.0</h2>

- Added centralized project metadata through `project.json`.
- Added `app/project.py` to load project metadata from a single source of truth.
- Added `/version` endpoint exposing service metadata, version, contract version, repository and image.
- Added `version` and `contract_version` fields to `/health`.
- Added `version` and `contract_version` fields to `/ready`.
- Updated FastAPI metadata to use `project.json` for application title and version.
- Removed service name and API version from environment-driven runtime configuration.
- Removed `APP_NAME` from example environment files.
- Kept `app/version.py` as a backward-compatible metadata bridge.
- Added compatibility metadata through `compatibility.json`.
- Added machine-readable compatibility information for Core, AntiSpoof and JS SDK.
- Added compatibility checks validating alignment between `project.json` and `compatibility.json`.
- Added version contract tests for `/health`, `/ready`, `/version`, project metadata and compatibility metadata.
- Added release metadata checks to ensure Git tags match `project.json`.
- Added generated documentation blocks for health, readiness, version and compatibility examples.
- Added README documentation generation through `scripts/update_readme_examples.py`.
- Added usage documentation generation through `scripts/update_docs_usage.py`.
- Added compatibility documentation generation through `scripts/update_docs_compatibility.py`.
- Added project metadata validation through `scripts/check_project_metadata.py`.
- Added compatibility metadata validation through `scripts/check_compatibility_metadata.py`.
- Added release metadata validation through `scripts/check_release_metadata.py`.
- Added `docs/compatibility.md` for contract stability, versioning and compatibility rules.
- Added unified CI graph with quality, metadata, tests, contract compatibility and Docker runtime jobs.
- Added quality checks with Ruff linting, Ruff formatting and Python compilation.
- Added `requirements.dev.txt` for development and quality tooling.
- Added EditorConfig-based whitespace normalization.
- Added VS Code workspace settings for save-time formatting and whitespace cleanup and extension recommendations.
- Added generated documentation synchronization checks in CI.
- Added Docker runtime endpoint checks for `/health`, `/ready` and `/version`.
- Updated `.dockerignore` and `.gitignore` to align Docker builds with metadata, documentation and model binary policy.
- Updated README, usage, API contract and contributing documentation for v2.1.0 metadata and compatibility rules.
- Reformatted Python source and tests with Ruff.

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

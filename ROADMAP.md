<h1>Age Decision API Roadmap</h1>

This document tracks the public roadmap of Age Decision API.

<h2>Versioning Strategy</h2>

Age Decision API follows semantic versioning:

```text
vX.Y.Z
```

Meaning:

- `X` changes for major architectural or trust model changes
- `Y` changes for feature releases
- `Z` changes for patches, automation, documentation, CI, distribution, and maintenance

Examples:

```text
v1.0.1 -> automation and distribution patch
v1.1.0 -> API reliability and validation improvements
v2.0.0 -> trust and proof verification milestone
```

<h2>Roadmap</h2>

<h3>v1.0.0 - Credona Initial Public Release</h3>

- [x] Base64 verification endpoint
- [x] Core + Antispoof orchestration
- [x] Cred score aggregation
- [x] Privacy metadata
- [x] ZK-ready contract
- [x] Structured logging
- [x] Unit tests
- [x] Local Docker development setup
- [x] Request ID support
- [x] Correlation ID support
- [x] Health endpoint
- [x] Readiness endpoint
- [x] Apache License 2.0
- [x] README documentation

<h3>v1.0.1 - Automation and Distribution</h3>

- [x] Add GitHub Actions CI
- [x] Add automated tests on pull requests
- [x] Add Docker image build
- [x] Add automated release workflow
- [x] Add automated tag-based release notes
- [x] Publish Docker image through GHCR
- [x] Add CodeQL scanning
- [x] Add Dependabot configuration
- [x] Add production Dockerfile
- [x] Add image-based docker-compose.yml
- [x] Add `.env.example.dev`
- [x] Remove API_VERSION from runtime environment
- [x] Add single source of truth for application version
- [x] Add README badges
- [x] Align repository structure with core and antispoof
- [x] Document Docker image usage
- [x] Document automation workflows

<h3>v1.x - API Improvements</h3>

- [ ] Add rate limiting
- [ ] Add authentication with API keys
- [ ] Add JWT authentication option
- [ ] Add metrics with Prometheus
- [ ] Add distributed tracing
- [ ] Add error normalization
- [ ] Add stricter payload validation
- [ ] Add image size constraints
- [ ] Add request body size limits
- [ ] Add timeout-specific error responses
- [ ] Add downstream retry strategy
- [ ] Add OpenAPI examples
- [ ] Add integration tests with real Docker services

<h3>v2 - Trust and Identity</h3>

- [ ] Real Zero-Knowledge proof generation
- [ ] Tokenized identity / cred reuse
- [ ] Proof verification endpoint
- [ ] External verifier integration
- [ ] Signed verification result prototype
- [ ] Reusable Credona score envelope
- [ ] Proof-friendly metadata standardization
- [ ] External verification example

<h3>v3 - Production Trust Layer</h3>

- [ ] Multi-tenant API key management
- [ ] Usage quotas
- [ ] Audit-safe event model
- [ ] Stronger privacy-first guarantees
- [ ] Verifiable decision claims
- [ ] Partner integration SDK examples
- [ ] Production deployment reference architecture

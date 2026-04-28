<h1>Contributing to Age Decision API</h1>

This repository contains the public API gateway.

For global contribution rules, see:

```text
https://github.com/credona/age-decision/blob/main/CONTRIBUTING.md
```

<hr>

<h2>Local setup</h2>

```bash
cp .env.example.dev .env
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d --build
```

<hr>

<h2>Run tests</h2>

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api pytest
```

<hr>

<h2>Run quality checks</h2>

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api ruff check .
docker compose -f docker-compose.dev.yml exec age-decision-api ruff format --check .
docker compose -f docker-compose.dev.yml exec age-decision-api python scripts/check_project_metadata.py
docker compose -f docker-compose.dev.yml exec age-decision-api python scripts/check_compatibility_metadata.py
```

<hr>

<h2>Update generated documentation</h2>

Some documentation blocks are generated from `project.json` and `compatibility.json`.

Run:

```bash
docker compose -f docker-compose.dev.yml exec age-decision-api python scripts/update_readme_examples.py
docker compose -f docker-compose.dev.yml exec age-decision-api python scripts/update_docs_usage.py
docker compose -f docker-compose.dev.yml exec age-decision-api python scripts/update_docs_compatibility.py
```

Generated blocks are delimited by comments such as:

```text
<!-- BEGIN:HEALTH_RESPONSE -->
<!-- END:HEALTH_RESPONSE -->
```

Do not edit generated blocks manually.

<hr>

<h2>Contribution scope</h2>

Good API contributions include:

- response contract improvements
- request validation improvements
- downstream error normalization
- timeout and retry handling
- privacy metadata improvements
- OpenAPI contract tests
- integration tests with real services
- documentation updates

<hr>

<h2>Rules</h2>

Do not commit:

- credentials
- raw user images
- biometric templates
- local secrets
- generated cache folders
- production environment files

<hr>

<h2>Project metadata policy</h2>

Project identity metadata must be edited in:

```text
project.json
```

Compatibility metadata must be edited in:

```text
compatibility.json
```

Do not duplicate the service name, application name, version or contract version in environment files.

Release tags must match the version declared in `project.json`.

Example:

```text
project.json version: 2.1.0
Git tag: v2.1.0
```

<hr>

<h2>Documentation</h2>

Use:

- README.md for the repository entry point
- docs/usage.md for gateway usage
- docs/api-contract.md for public API contract
- docs/compatibility.md for compatibility and contract stability rules
- CHANGELOG.md for release history

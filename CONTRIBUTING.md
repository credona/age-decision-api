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

<h2>Documentation</h2>

Use:

- README.md for the repository entry point
- docs/usage.md for gateway usage
- docs/api-contract.md for public API contract
- CHANGELOG.md for release history

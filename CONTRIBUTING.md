<h1>Contributing to Age Decision API</h1>

This repository contains the public API gateway.

Global contributing policy:
https://github.com/credona/age-decision/blob/main/CONTRIBUTING.md

<hr>

<h2>Local setup</h2>

Start the full development stack:

~~~bash
./scripts/docker/dev.sh
~~~

The stack starts:

- `age-decision-core`
- `age-decision-antispoof`
- `age-decision-api`

<hr>

<h2>Developer workflow</h2>

Auto-fix, regenerate generated files, run tests, then run the final check:

~~~bash
./scripts/ci/fix_all_docker.sh
~~~

Run validation only:

~~~bash
./scripts/ci/check_all_docker.sh
~~~

Prepare a release locally:

~~~bash
docker compose --env-file .generated/compose/dev.env -f docker-compose.dev.yml exec age-decision-api scripts/ci/release_prepare.sh
~~~

<hr>

<h2>Configuration policy</h2>

Project metadata and default runtime values are edited in:

~~~text
project.json
~~~

Generated files are written under:

~~~text
.generated/
~~~

Do not edit generated files manually.

Do not commit `.env` files.

Do not duplicate the service name, application name, version, contract version, Docker image metadata, or default runtime values in environment files.

Compatibility metadata is synchronized from `project.json`.

Release tags must match the version declared in `project.json`.

Example:

~~~text
project.json version: 2.2.1
Git tag: v2.2.1
~~~

<hr>

<h2>Generated documentation</h2>

Some documentation blocks are generated from `project.json` and `compatibility.json`.

Generated blocks are delimited by comments such as:

~~~text
<!-- BEGIN:HEALTH_RESPONSE -->
<!-- END:HEALTH_RESPONSE -->
~~~

Do not edit generated blocks manually.

Use:

~~~bash
./scripts/ci/fix_all_docker.sh
~~~

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
- developer workflow improvements
- release automation improvements

<hr>

<h2>Rules</h2>

Do not commit:

- credentials
- raw user images
- biometric templates
- local secrets
- generated cache folders
- production environment files
- generated `.env` files

<hr>

<h2>Documentation</h2>

Use:

- README.md for the repository entry point
- docs/usage.md for gateway usage
- docs/api-contract.md for public API contract
- docs/compatibility.md for compatibility and contract stability rules
- CHANGELOG.md for release history

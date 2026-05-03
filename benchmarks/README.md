# API Benchmarks

This directory contains Age Decision API end-to-end benchmark tooling for v2.6.0.

## Scope

API benchmarks measure:

- public `/verify` latency
- public decision distribution
- spoof check presence
- end-to-end orchestration behavior
- privacy-safe report generation

## Privacy

Reports must never expose:

- image_base64
- raw image payloads
- downstream raw responses
- raw scores
- internal thresholds
- score components
- model paths

Only aggregate metrics are allowed.

## Run

Start API, core, and antispoof services first.

Then run:

scripts/benchmark/run_api_e2e_benchmark.sh

## Output

Default output:

benchmarks/reports/api-e2e-benchmark.json

The report must follow:

benchmarks/schemas/benchmark-report.schema.json

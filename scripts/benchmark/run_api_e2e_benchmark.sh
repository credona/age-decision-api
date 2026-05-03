#!/usr/bin/env sh
set -eu

URL="${BENCHMARK_API_URL:-http://localhost:8002/verify}"
INPUT_FILE="${BENCHMARK_INPUT_FILE:-test-face.jpg}"
ITERATIONS="${BENCHMARK_ITERATIONS:-20}"
TIMEOUT="${BENCHMARK_TIMEOUT:-10}"
OUTPUT_PATH="${BENCHMARK_OUTPUT_PATH:-benchmarks/reports/api-e2e-benchmark.json}"

python -m benchmarks.e2e.run_api_benchmark \
  --url "$URL" \
  --input-file "$INPUT_FILE" \
  --iterations "$ITERATIONS" \
  --timeout "$TIMEOUT" \
  --output "$OUTPUT_PATH"

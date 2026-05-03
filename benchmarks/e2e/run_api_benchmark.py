from __future__ import annotations

import argparse
import base64
import time
from pathlib import Path

import requests

from benchmarks.common.report import build_benchmark_report, write_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Age Decision API end-to-end benchmark."
    )
    parser.add_argument("--url", default="http://localhost:8002/verify")
    parser.add_argument("--input-file", default="test-face.jpg")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--output", default="benchmarks/reports/api-e2e-benchmark.json")
    return parser.parse_args()


def run_api_benchmark(args: argparse.Namespace) -> dict[str, object]:
    input_bytes = Path(args.input_file).read_bytes()
    encoded_input = base64.b64encode(input_bytes).decode("ascii")

    durations_ms: list[float] = []
    decisions: list[str] = []
    spoof_check_required_values: list[bool] = []

    for index in range(args.iterations):
        start = time.perf_counter()
        response = requests.post(
            args.url,
            json={
                "input_type": "image",
                "image_base64": encoded_input,
            },
            headers={
                "X-Request-ID": f"benchmark-api-e2e-{index}",
                "X-Correlation-ID": "benchmark-api-e2e",
            },
            timeout=args.timeout,
        )
        durations_ms.append((time.perf_counter() - start) * 1000)

        response.raise_for_status()
        payload = response.json()

        decisions.append(str(payload.get("decision", "deny")))
        spoof_check_required_values.append("spoof_check" in payload)

    return build_benchmark_report(
        durations_ms=durations_ms,
        decisions=decisions,
        spoof_check_required_values=spoof_check_required_values,
        command=(
            "python -m benchmarks.e2e.run_api_benchmark "
            f"--url {args.url} --input-file <redacted> "
            f"--iterations {args.iterations} --timeout {args.timeout} --output {args.output}"
        ),
        sample_count=args.iterations,
    )


def main() -> None:
    args = parse_args()
    report = run_api_benchmark(args)
    write_report(report, args.output)
    print(f"Benchmark report written to {args.output}")


if __name__ == "__main__":
    main()

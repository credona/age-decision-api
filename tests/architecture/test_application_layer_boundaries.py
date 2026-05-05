from pathlib import Path


def test_application_layer_does_not_import_infrastructure_or_http_clients():
    violations = []

    for path in Path("app/application").rglob("*.py"):
        source = path.read_text()

        for forbidden in (
            "app.infrastructure",
            "import httpx",
            "from app.infrastructure",
        ):
            if forbidden in source:
                violations.append(f"{path}: {forbidden}")

    assert not violations, "\n".join(violations)

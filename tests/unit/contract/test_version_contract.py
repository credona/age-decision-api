import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def load_project() -> dict:
    return json.loads(Path("project.json").read_text(encoding="utf-8"))


def test_project_and_compatibility_versions_are_aligned():
    project = load_project()
    compatibility = json.loads(Path("compatibility.json").read_text(encoding="utf-8"))

    assert compatibility["service"] == project["service_name"]
    assert compatibility["version"] == project["version"]
    assert compatibility["contract_version"] == project["contract_version"]


def test_health_exposes_contract_version():
    project = load_project()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["contract_version"] == project["contract_version"]


def test_ready_exposes_contract_version(monkeypatch):
    project = load_project()

    async def fake_readiness():
        return {
            "core": {
                "status": "ready",
                "url": "http://age-decision-core:8000",
            },
            "antispoof": {
                "status": "ready",
                "url": "http://age-decision-antispoof:8001",
            },
        }

    from app.services.decision_service import decision_service

    monkeypatch.setattr(decision_service, "readiness", fake_readiness)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["version"] == project["version"]
    assert response.json()["contract_version"] == project["contract_version"]


def test_version_endpoint_exposes_project_version():
    project = load_project()

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["version"] == project["version"]
    assert response.json()["contract_version"] == project["contract_version"]

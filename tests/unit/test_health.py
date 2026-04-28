import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    project = json.loads(Path("project.json").read_text(encoding="utf-8"))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": project["service_name"],
        "version": project["version"],
        "contract_version": project["contract_version"],
    }

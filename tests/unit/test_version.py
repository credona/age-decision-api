from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_version_returns_project_metadata():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "service_name": "age-decision-api",
        "app_name": "Age Decision API",
        "version": "2.1.0",
        "contract_version": "2.0",
        "repository": "https://github.com/credona/age-decision-api",
        "image": "ghcr.io/credona/age-decision-api",
    }

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data == {
        "status": "ok",
        "service": "age-decision-api",
        "version": "2.1.0",
        "contract_version": "2.0",
    }

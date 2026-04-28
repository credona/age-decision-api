from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ready():
    response = client.get("/ready")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "core" in data
    assert "antispoof" in data

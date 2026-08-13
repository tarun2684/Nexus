from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "Nexus"


def test_health_shape():
    # Doesn't require live DB/Redis — just checks the endpoint responds
    # with the right shape, degraded or not.
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"status", "db", "redis"}
    assert body["status"] in {"ok", "degraded"}

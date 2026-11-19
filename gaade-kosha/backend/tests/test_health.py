from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    """Verify /health returns 200 OK and expected payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Gaade Kosha API"
    assert data["version"] == "0.1.0"
    assert "Hello World" in data["message"]


def test_root_endpoint():
    """Verify root endpoint returns 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Gaade Kosha" in data["message"]


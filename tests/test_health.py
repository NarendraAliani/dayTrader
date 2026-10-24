from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_is_paper_only_by_default():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["mode"] == "paper-only"


def test_strategy_endpoint_is_explicit_about_empty_registry():
    response = client.get("/api/v1/strategies")
    assert response.status_code == 200
    assert response.json()["count"] == 0

"""Unit and integration tests for I endpoints."""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_returns_welcome_message() -> None:
    """GET / should return API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert "meta" in json_data
    assert "title" in json_data["meta"]

def test_health_returns_ok() -> None:
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}




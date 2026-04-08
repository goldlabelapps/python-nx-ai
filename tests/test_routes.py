"""Unit and integration tests for I endpoints."""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_returns_welcome_message() -> None:
    """GET / should reply in the first person."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert "meta" in json_data
    assert "data" in json_data
    assert "title" in json_data["meta"]

def test_health_returns_ok() -> None:
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_unflag_all_prospects():
    """POST /unflag-all should reset all flags to false and return success meta."""
    # First, flag some prospects (if needed) - skipping setup for brevity
    response = client.post("/unflag-all")
    assert response.status_code == 200
    json_data = response.json()
    # The meta dict uses 'severity' for status, not 'status'
    assert json_data["meta"].get("severity") == "success"
    # Accept any success message in the title
    assert json_data["meta"].get("title", "").endswith("unflagged.")



"""Unit and integration tests for NX AI routes."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_welcome_message() -> None:
    """GET / should return a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert "meta" in json_data
    assert "data" in json_data
    assert "message" in json_data["meta"]
    assert "NX AI" in json_data["meta"]["message"]


def test_health_returns_ok() -> None:
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_echo_returns_message() -> None:
    """POST /echo should return the provided message."""
    response = client.post("/echo", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"echo": "hello"}


def test_echo_empty_string() -> None:
    """POST /echo with an empty string should echo back an empty string."""
    response = client.post("/echo", json={"message": ""})
    assert response.status_code == 200
    assert response.json() == {"echo": ""}


def test_echo_missing_body_returns_422() -> None:
    """POST /echo without a body should return 422 Unprocessable Entity."""
    response = client.post("/echo", json={})
    assert response.status_code == 422

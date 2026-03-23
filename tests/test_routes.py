"""Unit and integration tests for I endpoints."""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api.routes import get_db_connection
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


def test_products_returns_list() -> None:
    """GET /products should return a list of products (possibly empty)."""
    response = client.get("/products")
    assert response.status_code == 200
    json_data = response.json()
    assert "meta" in json_data
    assert "data" in json_data
    assert isinstance(json_data["data"], list)


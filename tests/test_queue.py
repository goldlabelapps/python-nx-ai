import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_queue():
    response = client.get("/queue")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "data" in data
    queue_data = data["data"]
    assert "in_queue" in queue_data
    assert "collections" in queue_data
    assert "groups" in queue_data
    assert "filtered" in queue_data
    assert "total" in queue_data
    assert "next" in queue_data
    meta = data["meta"]
    assert meta["severity"] == "success"
    assert meta["title"] == "Queue table info"

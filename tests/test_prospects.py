import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_prospects_root():
    response = client.get("/prospects")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "data" in data
    assert isinstance(data["data"], list)
    # Check that the expected keys are present in the data list
    assert any("init" in item for item in data["data"])
    assert any("search" in item for item in data["data"])
    # Meta checks
    meta = data["meta"]
    assert meta["severity"] == "success"
    assert meta["title"] == "Prospects endpoint"

def test_prospects_returns_list():
    response = client.get("/prospects")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "data" in data
    assert isinstance(data["data"], list) or isinstance(data["data"], dict)

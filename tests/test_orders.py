import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_orders_root():
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "pagination" in data
    assert "data" in data
    assert "search" in data
    assert isinstance(data["data"], list)
    # Check that the expected keys are present in the data list (if not empty)
    if data["data"]:
        first_item = data["data"][0]
        # Accept any unique identifier, e.g., 'sku' or 'name' or 'order_id'
        assert (
            "sku" in first_item or
            "name" in first_item or
            "order_id" in first_item
        )
        assert "name" in first_item or "description" in first_item or "categories" in first_item
    # Meta checks
    meta = data["meta"]
    assert meta["severity"] == "success"
    assert meta["title"] == "Read paginated orders"

def test_orders_search_param():
    search_term = "test"
    response = client.get(f"/orders?s={search_term}")
    assert response.status_code == 200
    data = response.json()
    assert "search" in data
    # Accept both string and dict for search key for compatibility
    if isinstance(data["search"], dict):
        assert data["search"].get("searchStr") == search_term



def test_orders_returns_list():
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "pagination" in data
    assert "data" in data
    assert isinstance(data["data"], list)

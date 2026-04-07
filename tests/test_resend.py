import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_resend_post_email(monkeypatch):
    """Test POST /resend actually sends an email if RESEND_API_KEY is set."""
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        pytest.skip("RESEND_API_KEY not set; skipping real email test.")

    payload = {
        "to": 'listingslab@gmail.com',
        "subject": "pytest",
        "html": "Python tests have run"
    }
    response = client.post("/resend", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "meta" in data
    assert data["meta"]["severity"] == "success"
    assert "Email sent successfully" in data["meta"]["title"]
    assert "data" in data
    assert "id" in data["data"] or "object" in data["data"]

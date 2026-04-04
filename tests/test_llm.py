import os
import pytest
def test_llm_real_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not set; skipping real LLM API test.")
    from google import genai
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents="Say hello from Gemini!"
        )
        completion = getattr(response, "text", None)
        assert completion is not None and "hello" in completion.lower()
    except Exception as e:
        pytest.fail(f"LLM real API call failed: {e}")
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)




def test_llm_get_endpoint():
    response = client.get("/llm")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert data["meta"]["severity"] == "success"
    assert "LLM" in data["meta"]["title"]
    assert "records" in data["meta"]["title"]


def test_llm_post_endpoint(monkeypatch):
    # Mock google-genai SDK to avoid real API call
    class MockGenAIResponse:
        text = "Test completion"

    class MockGenAIModel:
        def generate_content(self, model, contents):
            return MockGenAIResponse()

    class MockGenAIClient:
        models = MockGenAIModel()

    monkeypatch.setattr("google.genai.Client", lambda *args, **kwargs: MockGenAIClient())

    payload = {"prompt": "Test prompt"}
    response = client.post("/llm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert data["meta"]["severity"] == "success"
    assert "completion received" in data["meta"]["title"]
    assert data["data"]["prompt"] == "Test prompt"
    assert data["data"]["completion"] == "Test completion"
    assert "data" in data
    assert data["data"]["prompt"] == "Test prompt"
    assert data["data"]["completion"] == "Test completion"

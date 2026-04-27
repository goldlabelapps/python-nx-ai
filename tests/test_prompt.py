import json
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class _MockCursor:
    def __init__(self, fetchone_values):
        self._fetchone_values = list(fetchone_values)
        self._fetchall_values = []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        if self._fetchone_values:
            return self._fetchone_values.pop(0)
        return None

    def fetchall(self):
        if self._fetchall_values:
            return self._fetchall_values.pop(0)
        return []

    def close(self):
        return None


class _MockConnection:
    def __init__(self, fetchone_values):
        self.cursor_obj = _MockCursor(fetchone_values)
        self.committed = False

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        self.committed = True

    def close(self):
        return None


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeModels:
    def generate_content(self, model, contents):
        return _FakeResponse(f"fresh completion for: {contents}")


class _FakeGenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.models = _FakeModels()


def test_prompt_get_includes_top_record(monkeypatch):
    conn = _MockConnection(
        fetchone_values=[
            (5,),
            (501, "Latest prompt", "Latest completion", datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc), "models/gemini-1.5-pro"),
        ]
    )
    conn.cursor_obj._fetchall_values = [[("id",), ("prompt",), ("completion",), ("time",), ("model",)]]

    from app.api.prompt import prompt as prompt_module

    monkeypatch.setattr(prompt_module, "get_db_connection_direct", lambda: conn)

    response = client.get("/prompt")
    assert response.status_code == 200

    payload = response.json()
    assert payload["meta"]["severity"] == "success"
    assert payload["data"]["record_count"] == 5
    assert payload["data"]["columns"] == ["id", "prompt", "completion", "time", "model"]
    assert payload["data"]["top_record"] == {
        "id": 501,
        "prompt": "Latest prompt",
        "completion": "Latest completion",
        "time": "2026-04-27T12:00:00+00:00",
        "model": "models/gemini-1.5-pro",
    }


def test_prompt_post_returns_cached_response(monkeypatch):
    # Keep auth open for tests and avoid needing a real API key.
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    # 1) search_vector column exists
    # 2) exact cache row found by prompt hash / prompt
    conn = _MockConnection(
        fetchone_values=[
            (True,),
            (101, "Who is Ada Lovelace?", "Cached answer", None, "models/gemini-1.5-pro"),
        ]
    )

    from app.api.prompt import prompt as prompt_module

    monkeypatch.setattr(prompt_module, "get_db_connection_direct", lambda: conn)

    response = client.post("/prompt", json={"prompt": "Who is Ada Lovelace?"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["meta"]["severity"] == "success"
    assert payload["data"]["cached"] is True
    assert payload["data"]["prompt_id"] == 101
    assert payload["data"]["completion"] == "Cached answer"

    # Ensure only lookup queries ran; no insert commit should happen.
    assert conn.committed is False


def test_prompt_post_cache_miss_calls_gemini_and_saves(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    # 1) search_vector column exists
    # 2) no exact cache row
    # 3) no tsvector fallback cache row
    # 4) insert returning id
    conn = _MockConnection(
        fetchone_values=[
            (True,),
            None,
            None,
            (202,),
        ]
    )

    from app.api.prompt import prompt as prompt_module

    monkeypatch.setattr(prompt_module, "get_db_connection_direct", lambda: conn)

    # Patch google.genai client constructor used in route.
    import google.genai as genai

    monkeypatch.setattr(genai, "Client", _FakeGenAIClient)

    response = client.post("/prompt", json={"prompt": "Explain quicksort"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["meta"]["severity"] == "success"
    assert payload["data"]["cached"] is False
    assert payload["data"]["id"] == 202
    assert payload["data"]["prompt"] == "Explain quicksort"
    assert payload["data"]["completion"].startswith("fresh completion for: Explain quicksort")

    # Insert path should commit.
    assert conn.committed is True


def test_prompt_post_missing_prompt_returns_400():
    response = client.post("/prompt", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing 'prompt' in request body."


def test_prompt_delete_id_deletes_matching_record(monkeypatch):
    conn = _MockConnection(
        fetchone_values=[
            (303, "Ada Lovelace"),
            (303,),
        ]
    )

    from app.api.prompt import delete_id as delete_module

    monkeypatch.setattr(delete_module, "get_db_connection_direct", lambda: conn)

    response = client.delete("/prompt/delete_id?id=303")
    assert response.status_code == 200

    payload = response.json()
    assert payload["meta"]["severity"] == "success"
    assert payload["data"]["id"] == 303
    assert payload["data"]["prompt"] == "Ada Lovelace"
    assert conn.committed is True


def test_prompt_delete_id_returns_error_when_missing(monkeypatch):
    conn = _MockConnection(fetchone_values=[None])

    from app.api.prompt import delete_id as delete_module

    monkeypatch.setattr(delete_module, "get_db_connection_direct", lambda: conn)

    response = client.delete("/prompt/delete_id?id=999")
    assert response.status_code == 200

    payload = response.json()
    assert payload["meta"]["severity"] == "error"
    assert payload["data"] == {}
    assert conn.committed is False


def test_prompt_delete_id_requires_query_string_id():
    response = client.delete("/prompt/delete_id")
    assert response.status_code == 422

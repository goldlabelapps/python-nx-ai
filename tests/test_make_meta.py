import os
import re
import time
import pytest
from app.utils.make_meta import make_meta
from app import __version__

def test_make_meta_basic(monkeypatch):
    monkeypatch.setenv("BASE_URL", "http://testserver:9000")
    before = int(time.time() * 1000)
    meta = make_meta("info", "Test Title")
    after = int(time.time() * 1000)
    assert meta["severity"] == "info"
    assert meta["title"] == "Test Title"
    assert meta["version"] == __version__
    assert meta["base"] == "http://testserver:9000"
    assert before <= meta["time"] <= after

def test_make_meta_default_base_url(monkeypatch):
    monkeypatch.delenv("BASE_URL", raising=False)
    meta = make_meta("success", "Default URL")
    assert meta["base"] == "http://localhost:8000"

def test_make_meta_time_is_int():
    meta = make_meta("info", "Time Test")
    assert isinstance(meta["time"], int)
    assert re.match(r"^\d{13}$", str(meta["time"]))

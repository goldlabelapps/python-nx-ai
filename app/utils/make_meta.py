import os
import time
from app import __version__

def make_meta(severity: str, message: str) -> dict:
    """Creates a standard meta dictionary for API responses."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    epoch = int(time.time() * 1000)
    return {
        "version": __version__,
        "time": epoch,
        "severity": severity,
        "title": message,
        "message": message,
        "base": base_url,
    }

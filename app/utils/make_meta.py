import os
import time
from app import __version__

def make_meta(severity: str, title: str) -> dict:
    """Create a standard meta dictionary for API responses."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    epoch = int(time.time() * 1000)
    return {
        "severity": severity,
        "title": title,
        "version": __version__,
        "endpoint": f"{base_url}/prospects",
        "base": base_url,
        "base_url": base_url,
        "message": title,
        "time": epoch,
    }

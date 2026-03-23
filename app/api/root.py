from app import __version__
from fastapi import APIRouter
import os, time
from dotenv import load_dotenv
from app import __version__

router = APIRouter()

@router.get("/")
def root() -> dict:
    """Return product data."""
    load_dotenv()
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    epoch = int(time.time() * 1000)
    meta = {
        "severity": "success",
        "title": "NX-AI says hi",
        "version": __version__,
        "base_url": base_url,
        "time": epoch,
    }
    endpoints = [
        {"name": "docs", "url": f"{base_url}/docs"},
        {"name": "health", "url": f"{base_url}/health"},
        {"name": "products", "url": f"{base_url}/products"}
    ]
    return {"meta": meta, "data": endpoints}

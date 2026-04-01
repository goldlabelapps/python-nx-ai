
from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path
from app.utils.db import get_db_connection

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")

@router.get("/prompts")
def root() -> dict:
    """GET /prospects endpoint."""
    meta = make_meta("success", "Prompts endpoint")
    data = [
        {"init": f"{base_url}/prompts"},
    ]
    return {"meta": meta, "data": data}

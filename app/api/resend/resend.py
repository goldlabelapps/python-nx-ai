
from app import __version__
import os
from app.utils.make_meta import make_meta

from fastapi import APIRouter, Query, Path, Body, HTTPException

from app.utils.db import get_db_connection


router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

@router.get("/resend")
def root() -> dict:
    """GET /resend endpoint."""
    if not RESEND_API_KEY:
        meta = make_meta("error", "RESEND_API_KEY is missing from environment. Please set it in your .env file.")
        return {"meta": meta}
    meta = make_meta("success", "Resend endpoint")
    data = [
        {"action,": f"send email"},
    ]
    return {"meta": meta, "data": data}

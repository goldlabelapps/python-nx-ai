import os
from fastapi import Request, HTTPException, status
from app.utils.make_meta import make_meta
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PYTHON_KEY")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(request: Request, api_key_header: Optional[str] = ""):
    if API_KEY is None:
        meta = make_meta("error", "PYTHON_KEY not set")
        return {"meta": meta, "data": []}
    if api_key_header == API_KEY:
        return api_key_header
    else:
        meta = make_meta("error", "Invalid PYTHON_KEY Key")
        return {"meta": meta, "data": []}

import os
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()


@router.get("/queue")
def read_queue() -> dict:
    """GET /queue: """
    return {"meta": make_meta("success", "Hello from queue"), "data": {"do": "it"}}

    

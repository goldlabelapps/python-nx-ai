import os
import hashlib
from fastapi import APIRouter, HTTPException, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.get("/github")
def get_github(api_key: str = Depends(get_api_key)) -> dict:
    """GET /github: Return GitHub data."""
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM github;")
        count_row = cur.fetchone()
        record_count = count_row[0] if count_row and count_row[0] is not None else 0
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'github'
            ORDER BY ordinal_position;
            """
        )
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        meta = make_meta("success", "GitHub table metadata")
        return {
            "meta": meta,
            "data": {
                "record_count": record_count,
                "columns": columns,
            },
        }
    except Exception as e:
        meta = make_meta("error", f"DB error: {str(e)}")
        return {"meta": meta, "data": {}}

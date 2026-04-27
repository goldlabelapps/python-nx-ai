"""Empty all GitHub tables."""

from fastapi import APIRouter, HTTPException, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

_TABLES = [
    "github_accounts",
    "github_repos",
    "github_gists",
    "github_projects",
    "github_resources",
]


@router.post("/api/github/empty")
def empty_github_tables(api_key: str = Depends(get_api_key)) -> dict:
    """POST /api/github/empty: Truncate all GitHub tables."""
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        for table in _TABLES:
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
        conn.commit()
        return {"meta": make_meta("success", "All GitHub tables emptied"), "data": {"tables": _TABLES}}
    except Exception as e:
        if conn is not None:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

from fastapi import APIRouter, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

_TABLES = [
    "youtube_channels",
    "youtube_videos",
    "youtube_playlists",
    "youtube_resources",
]

def _fetch_table(cur, table: str) -> dict:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    row = cur.fetchone()
    count = row[0] if row and row[0] is not None else 0
    cur.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 100;")
    if cur.description:
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]
    else:
        rows = []
    return {"count": count, "rows": rows}


@router.get("/youtube")
def get_youtube(api_key: str = Depends(get_api_key)) -> dict:
    """GET /youtube: Return counts and records from all YouTube tables."""
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        data = {table: _fetch_table(cur, table) for table in _TABLES}
        return {"meta": make_meta("success", "YouTube data"), "data": data}
    except Exception as e:
        return {"meta": make_meta("error", f"DB error: {str(e)}"), "data": {}}
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

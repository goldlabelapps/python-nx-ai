from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.post("/flickr/emptytables")
def empty_flickr_tables(api_key: str = Depends(get_api_key)) -> dict:
    """POST /flickr/emptytables: Delete all rows from all Flickr tables."""
    tables = [
        "flickr_accounts",
        "flickr_photos",
        "flickr_albums",
        "flickr_resources"
    ]
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        for table in tables:
            cur.execute(f"DELETE FROM {table};")
        conn.commit()
        return {"meta": make_meta("success", "Flickr tables emptied"), "data": {}}
    except Exception as e:
        return {"meta": make_meta("error", f"DB error: {str(e)}"), "data": {}}
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

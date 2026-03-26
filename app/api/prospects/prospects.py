from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter
from app.utils.db import get_db_connection

router = APIRouter()

@router.get("/prospects")
def root() -> dict:
    """Return all prospects table records"""
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    actions = [
        {
            "name": "Seed prospects table",
            "url": f"{base_url}/prospects/seed"
        },
        {
            "name": "Empty prospects table",
            "url": f"{base_url}/prospects/empty"
        },
    ]
    try:
        cur.execute('SELECT * FROM prospects;')
        if cur.description is None:
            prospects = []
        else:
            columns = [desc[0] for desc in cur.description]
            prospects = [dict(zip(columns, row)) for row in cur.fetchall()]
        meta = make_meta("success", "Prospects List")
        result = {"meta": meta, "data": prospects}
    except Exception as e:
        import psycopg2
        if isinstance(e, psycopg2.errors.UndefinedTable):
            meta = make_meta("error", "prospects table does not exist.")
            result = {"meta": meta, "data": actions}
        else:
            meta = make_meta("error", str(e))
            result = {"meta": meta, "data": actions}
    finally:
        cur.close()
        conn.close()
    return result

from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.post("/flickr/createtable")
def create_flickr_tables(api_key: str = Depends(get_api_key)) -> dict:
    """POST /flickr/createtable: Create Flickr tables in Postgres."""
    sql_statements = [
        # Drop tables if they exist (in reverse dependency order)
        'DROP TABLE IF EXISTS flickr_resources;',
        'DROP TABLE IF EXISTS flickr_albums;',
        'DROP TABLE IF EXISTS flickr_photos;',
        'DROP TABLE IF EXISTS flickr_accounts;',
        '''CREATE TABLE IF NOT EXISTS flickr_accounts (
            id SERIAL PRIMARY KEY,
            flickr_id TEXT,
            username TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS flickr_photos (
            id SERIAL PRIMARY KEY,
            flickr_id TEXT UNIQUE,
            title TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS flickr_albums (
            id SERIAL PRIMARY KEY,
            flickr_id TEXT,
            title TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS flickr_resources (
            id SERIAL PRIMARY KEY,
            resource_type TEXT,
            flickr_id TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );'''
    ]
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        for stmt in sql_statements:
            cur.execute(stmt)
        conn.commit()
        return {"meta": make_meta("success", "Flickr tables created"), "data": {}}
    except Exception as e:
        return {"meta": make_meta("error", f"DB error: {str(e)}"), "data": {}}
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

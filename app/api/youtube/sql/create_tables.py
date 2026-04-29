from fastapi import APIRouter, Depends
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.post("/youtube/createtable")
def create_youtube_tables(api_key: str = Depends(get_api_key)) -> dict:
    """POST /youtube/createtable: Drop and create YouTube tables in Postgres."""
    sql_statements = [
        'DROP TABLE IF EXISTS youtube_resources;',
        'DROP TABLE IF EXISTS youtube_playlists;',
        'DROP TABLE IF EXISTS youtube_videos;',
        'DROP TABLE IF EXISTS youtube_channels;',
        '''CREATE TABLE IF NOT EXISTS youtube_channels (
            id SERIAL PRIMARY KEY,
            youtube_id TEXT UNIQUE,
            title TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS youtube_videos (
            id SERIAL PRIMARY KEY,
            youtube_id TEXT UNIQUE,
            title TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS youtube_playlists (
            id SERIAL PRIMARY KEY,
            youtube_id TEXT,
            title TEXT,
            payload JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS youtube_resources (
            id SERIAL PRIMARY KEY,
            resource_type TEXT,
            youtube_id TEXT,
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
        return {"meta": make_meta("success", "YouTube tables created"), "data": {}}
    except Exception as e:
        return {"meta": make_meta("error", f"DB error: {str(e)}"), "data": {}}
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

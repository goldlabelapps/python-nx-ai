import os
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.get("/queue")
def read_queue() -> dict:
    """GET /queue: Return queue table info, schema, and most recent record."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()

        # 1. Count records
        cursor.execute("SELECT COUNT(*) FROM queue;")
        count_row = cursor.fetchone()
        record_count = count_row[0] if count_row else 0

        # 2. Get table schema
        cursor.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'queue';")
        schema = [
            {
                "name": row[0],
                "type": row[1]
            }
            for row in cursor.fetchall()
        ]

        # 3. Get most recently updated record
        cursor.execute("SELECT * FROM queue ORDER BY updated DESC LIMIT 1;")
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        row = cursor.fetchone()
        most_recent = dict(zip(columns, row)) if row and columns else None

        conn.close()

        return {
            "meta": make_meta("success", "Queue table info"),
            "data": {
                "queued": record_count,
                "most_recent": most_recent,
                "schema": schema
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

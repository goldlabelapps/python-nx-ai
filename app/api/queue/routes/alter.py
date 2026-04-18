from fastapi import APIRouter, HTTPException, Body
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.post("/queue/alter/add-column")
def add_column_to_queue(
    column_name: str = Body(..., embed=True),
    column_type: str = Body(..., embed=True)
) -> dict:
    """POST /queue/alter/add-column: Add a new column to the queue table."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        sql = f'ALTER TABLE queue ADD COLUMN "{column_name}" {column_type};'
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return {"meta": make_meta("success", f"Column '{column_name}' added as {column_type}")}
    except Exception as e:
        msg = str(e)
        if 'already exists' in msg:
            return {"meta": make_meta("error", f"Column '{column_name}' exists")}
        raise HTTPException(status_code=500, detail=msg)

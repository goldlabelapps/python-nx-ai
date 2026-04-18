import os
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.delete("/queue/delete")
def delete_queue_record(id: int) -> dict:
    """DELETE /queue/delete: Delete a record from the queue table by id."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queue WHERE id = %s RETURNING id;", (id,))
        deleted = cursor.fetchone()
        conn.commit()
        conn.close()
        if deleted:
            return {"meta": make_meta("success", f"Record with id {id} deleted.")}
        else:
            return {"meta": make_meta("error", f"No record found with id {id}.")}
    except Exception as e:
        msg = str(e)
        return {"meta": make_meta("error", msg)}

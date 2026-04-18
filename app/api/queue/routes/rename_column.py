from fastapi import APIRouter, HTTPException, Body
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.post("/queue/alter/rename_column")
def rename_column(
    old_name: str = Body(..., embed=True),
    new_name: str = Body(..., embed=True),
    column_type: str = Body(..., embed=True)
) -> dict:
    """POST /queue/alter/rename_column: Rename a column in the queue table."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        sql = f'ALTER TABLE queue RENAME COLUMN "{old_name}" TO "{new_name}";'
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return {"meta": make_meta("success", f"Column '{old_name}' renamed to '{new_name}'")}
    except Exception as e:
        msg = str(e)
        if 'does not exist' in msg:
            raise HTTPException(status_code=400, detail=f"Column '{old_name}' does not exist in queue table.")
        if 'already exists' in msg:
            raise HTTPException(status_code=400, detail=f"Column '{new_name}' already exists in queue table.")
        raise HTTPException(status_code=500, detail=msg)

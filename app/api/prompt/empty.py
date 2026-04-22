from fastapi import APIRouter, Depends

from app.utils.api_key_auth import get_api_key
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta

router = APIRouter()

# PATCH /prompt/empty: empties the prompt table
@router.patch("/prompt/empty")
def empty_prompt_table(api_key: str = Depends(get_api_key)) -> dict:
    """PATCH /prompt/empty: empties the prompt table."""
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE prompt RESTART IDENTITY CASCADE;")
        conn.commit()
        cur.close()
        conn.close()
        return {"meta": make_meta("success", "Prompt table emptied"), "data": {}}
    except Exception as e:
        return {"meta": make_meta("error", f"Failed to empty prompt table: {str(e)}"), "data": {}}

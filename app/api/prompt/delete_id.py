from fastapi import APIRouter, Depends

from app.utils.api_key_auth import get_api_key
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta

router = APIRouter()


@router.delete("/prompt/delete_id")
def delete_prompt_by_id(id: int, api_key: str = Depends(get_api_key)) -> dict:
    """DELETE /prompt/delete_id: delete a prompt record by id."""
    conn = None
    cur = None
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, prompt
            FROM prompt
            WHERE id = %s
            LIMIT 1;
            """,
            (id,),
        )
        row = cur.fetchone()
        if not row:
            return {
                "meta": make_meta("error", f"id {id} not found"),
                "data": {},
            }

        cur.execute("DELETE FROM prompt WHERE id = %s RETURNING id;", (id,))
        deleted = cur.fetchone()
        conn.commit()
        if not deleted:
            return {
                "meta": make_meta("error", f"Failed to delete prompt record for id {id}."),
                "data": {},
            }

        return {
            "meta": make_meta("success", f"Deleted prompt record for id {id}."),
            "data": {"id": row[0], "prompt": row[1]},
        }
    except Exception as e:
        return {
            "meta": make_meta("error", f"Failed to delete prompt record: {str(e)}"),
            "data": {},
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
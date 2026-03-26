from fastapi import APIRouter, status
from app.utils.db import get_db_connection

router = APIRouter()

@router.delete("/prospects/empty", status_code=status.HTTP_200_OK)
def empty_prospects() -> dict:
    """Delete all records from the prospects table, leaving the structure intact. Handles missing table gracefully."""
    import psycopg2
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM prospects;')
        conn.commit()
        result = {"detail": "All records deleted from prospects table."}
    except psycopg2.errors.UndefinedTable:
        conn.rollback()
        result = {"detail": "Table 'prospects' does not exist. No records deleted."}
    except Exception as e:
        conn.rollback()
        result = {"detail": f"Error: {str(e)}"}
    finally:
        cur.close()
        conn.close()
    return result
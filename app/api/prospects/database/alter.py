from fastapi import APIRouter, status
from app.utils.db import get_db_connection

router = APIRouter()

@router.patch("/prospects/alter", status_code=status.HTTP_200_OK)
def alter_prospects_table() -> dict:
    """
    Checks if the 'prospects' table exists, then checks if the 'secondary_email' column exists.
    If both exist, attempts to drop the 'secondary_email' column and returns the result.
    """
    import psycopg2
    column_name = 'tertiary_email_verification_source'  # Change this variable to alter a different column
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        # Check if 'prospects' table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'prospects'
            );
        """)
        table_row = cur.fetchone()
        if table_row is None:
            result = {"detail": "Error: Could not fetch table existence result."}
            return result
        table_exists = table_row[0]
        if not table_exists:
            result = {"detail": "Table 'prospects' does not exist."}
            return result

        # Check if the column exists
        cur.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'prospects' AND column_name = %s
            );
        """, (column_name,))
        column_row = cur.fetchone()
        if column_row is None:
            result = {"detail": "Error: Could not fetch column existence result."}
            return result
        column_exists = column_row[0]
        if not column_exists:
            result = {"detail": f"Column '{column_name}' does not exist in 'prospects' table."}
            return result

        # Try to drop the column
        try:
            cur.execute(f'ALTER TABLE prospects DROP COLUMN {column_name};')
            conn.commit()
            result = {"detail": f"Column '{column_name}' dropped successfully from 'prospects' table."}
        except Exception as e:
            conn.rollback()
            result = {"detail": f"Failed to drop column: {str(e)}"}
    except Exception as e:
        conn.rollback()
        result = {"detail": f"Error: {str(e)}"}
    finally:
        cur.close()
        conn.close()
    return result
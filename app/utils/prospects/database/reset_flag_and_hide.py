# Script to reset all 'flag' and 'hide' values to false in the prospects table
from app.utils.db import get_db_connection

def reset_flag_and_hide():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute("UPDATE prospects SET flag = FALSE, hide = FALSE;")
        conn.commit()
        print("All 'flag' and 'hide' values reset to FALSE.")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    reset_flag_and_hide()

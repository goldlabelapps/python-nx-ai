"""
Script to print the column names of the prospects table for debugging.
"""
from app.utils.db import get_db_connection

def print_prospects_columns():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM prospects LIMIT 1;")
        columns = [desc[0] for desc in cur.description]
        print("Columns in prospects table:", columns)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print_prospects_columns()

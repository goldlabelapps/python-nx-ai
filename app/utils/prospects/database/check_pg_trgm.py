"""
Check if pg_trgm extension is enabled in the PostgreSQL database.
"""
import psycopg2
from app.utils.db import get_db_connection

def check_pg_trgm():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'pg_trgm';")
        result = cur.fetchone()
        if result:
            print("pg_trgm extension is ENABLED.")
        else:
            print("pg_trgm extension is NOT enabled.")
    except Exception as e:
        print(f"Failed to check pg_trgm: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_pg_trgm()

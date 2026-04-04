"""
Migration script to enable pg_trgm extension for fuzzy search support.
Run this script once to enable the extension in your PostgreSQL database.
"""
import psycopg2
from app.utils.db import get_db_connection

def enable_pg_trgm():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        conn.commit()
        print("pg_trgm extension enabled successfully.")
    except Exception as e:
        print(f"Failed to enable pg_trgm: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    enable_pg_trgm()

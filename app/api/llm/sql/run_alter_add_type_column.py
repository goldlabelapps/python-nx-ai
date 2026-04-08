# Run this script to add a 'type' column to the llm table if it doesn't exist
from app.utils.db import get_db_connection_direct

def add_type_column():
    conn = get_db_connection_direct()
    cur = conn.cursor()
    try:
        cur.execute("""
            ALTER TABLE llm ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'default';
        """)
        conn.commit()
        print("'type' column added to llm table (if not already present).")
    except Exception as e:
        print(f"Error adding 'type' column: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_type_column()

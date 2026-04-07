import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.utils.db import get_db_connection_direct

if __name__ == "__main__":
    sql = """
    ALTER TABLE llm ADD COLUMN IF NOT EXISTS prompt_code TEXT;
    """
    conn = get_db_connection_direct()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Migration complete: prompt_code column added to llm table.")

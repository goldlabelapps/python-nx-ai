import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.utils.db import get_db_connection_direct

if __name__ == "__main__":
    conn = get_db_connection_direct()
    cur = conn.cursor()

    # Step 1: Select 8 random ids
    cur.execute("SELECT id FROM prospects ORDER BY RANDOM() LIMIT 8;")
    ids = [row[0] for row in cur.fetchall()]
    print(f"Keeping these 8 ids: {ids}")

    # Step 2: Cascade delete llm records, then delete prospects
    if ids:
        format_strings = ','.join(['%s'] * len(ids))
        # First, delete llm records referencing prospects that will be deleted
        delete_llm_sql = f"DELETE FROM llm WHERE prospect_id NOT IN ({format_strings});"
        cur.execute(delete_llm_sql, ids)
        # Now delete the prospects
        delete_sql = f"DELETE FROM prospects WHERE id NOT IN ({format_strings});"
        cur.execute(delete_sql, ids)
        conn.commit()
        print(f"Deleted all prospects except ids: {ids}")
    else:
        print("No records found in prospects table.")

    cur.close()
    conn.close()

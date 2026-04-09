import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.utils.db import get_db_connection_direct

if __name__ == "__main__":
    sql = "ALTER TABLE prospects RENAME COLUMN primary_email_last_verified_at TO sell_by_date;"
    conn = get_db_connection_direct()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("Migration complete: primary_email_last_verified_at column renamed to sell_by_date in prospects table.")

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.utils.db import get_db_connection_direct

if __name__ == "__main__":
    sql = """
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns
    WHERE table_name = 'prospects'
    ORDER BY ordinal_position;
    """
    conn = get_db_connection_direct()
    cur = conn.cursor()
    cur.execute(sql)
    columns = cur.fetchall()
    cur.close()
    conn.close()
    for col in columns:
        print(col)

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.utils.db import get_db_connection_direct

def get_create_table_sql(table_name):
    conn = get_db_connection_direct()
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
    """, (table_name,))
    columns = cur.fetchall()
    cur.close()
    conn.close()

    lines = []
    for name, dtype, nullable, default in columns:
        line = f'    {name} {dtype.upper()}'
        if nullable == 'NO':
            line += ' NOT NULL'
        if default:
            line += f' DEFAULT {default}'
        lines.append(line)
    create_sql = f"CREATE TABLE {table_name} (\n" + ",\n".join(lines) + "\n);"
    return create_sql

if __name__ == "__main__":
    print(get_create_table_sql('prospects'))

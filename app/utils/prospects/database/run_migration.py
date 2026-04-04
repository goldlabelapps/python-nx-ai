# Run SQL migration to add 'flag' and 'hide' columns to prospects table
from app.utils.db import get_db_connection

SQL_PATH = "app/api/prospects/database/alter_add_flag_hide.sql"

def run_migration():
    with open(SQL_PATH, "r") as f:
        sql = f.read()
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print("Migration successful: 'flag' and 'hide' columns added.")
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migration()

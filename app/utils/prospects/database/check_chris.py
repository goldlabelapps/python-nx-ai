"""
Quick script to check if any prospects contain 'chris' in name, email, or company.
"""
def check_chris():

from app.utils.db import get_db_connection

def check_chris():
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, first_name, last_name, email, company_name FROM prospects
            WHERE (
                LOWER(first_name) LIKE '%chris%'
                OR LOWER(last_name) LIKE '%chris%'
                OR LOWER(email) LIKE '%chris%'
                OR LOWER(company_name) LIKE '%chris%'
            )
            AND hide IS NOT TRUE
            LIMIT 10;
        """)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print("No prospects found with 'chris' in first_name, last_name, email, or company_name.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()


import os, time
from fastapi import APIRouter, status
from app.utils.db import get_db_connection

router = APIRouter()

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/big.csv'))


import csv
import io

def normalize_column(col):
    import re
    col = col.strip().lower().replace(' ', '_')
    col = re.sub(r'[^a-z0-9_]', '', col)
    if col and col[0].isdigit():
        col = '_' + col
    return col

@router.put("/prospects/process", status_code=status.HTTP_200_OK)
def process_prospects() -> dict:
    """
    Process and insert data from the large CSV file (big.csv) into the prospects table.
    The table must already exist with the correct columns (run seed and empty first).
    This endpoint is robust and scalable for large files.
    """
    import psycopg2
    BATCH_SIZE = 200
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    inserted = 0
    try:
        with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            columns_raw = next(reader)
            remove_cols = {'secondary_email', 'secondary_email_source', 'secondary_email_status', 'secondary_email_verification_source'}
            columns = [normalize_column(col) for col in columns_raw if normalize_column(col) not in remove_cols]
            col_indices = [i for i, col in enumerate([normalize_column(col) for col in columns_raw]) if col not in remove_cols]
            placeholders = ', '.join(['%s'] * len(columns))
            batch = []
            for row in reader:
                filtered_row = [row[i] for i in col_indices]
                text_content = ' '.join([str(val) for val in filtered_row if val is not None])
                batch.append(filtered_row + [text_content])
                if len(batch) >= BATCH_SIZE:
                    cur.executemany(
                        f"INSERT INTO prospects ({', '.join(columns)}, search_vector) VALUES ({placeholders}, to_tsvector('english', %s))",
                        batch
                    )
                    inserted += len(batch)
                    batch = []
            if batch:
                cur.executemany(
                    f"INSERT INTO prospects ({', '.join(columns)}, search_vector) VALUES ({placeholders}, to_tsvector('english', %s))",
                    batch
                )
                inserted += len(batch)
        conn.commit()
        result = {"detail": f"Inserted {inserted} records from big.csv into prospects table."}
    except psycopg2.errors.UndefinedTable:
        conn.rollback()
        result = {"detail": "Table 'prospects' does not exist. No records inserted."}
    except Exception as e:
        conn.rollback()
        result = {"detail": f"Error: {str(e)}"}
    finally:
        cur.close()
        conn.close()
    return result
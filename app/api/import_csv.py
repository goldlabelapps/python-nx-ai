from fastapi import APIRouter, UploadFile, File, HTTPException

import csv
import psycopg2
import os
import io
from dotenv import load_dotenv

router = APIRouter()

@router.post("/import-csv")
def import_csv(file: UploadFile = File(...)):
    """Import products from a CSV file into the database."""
    load_dotenv()
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    try:
        reader = csv.DictReader(io.TextIOWrapper(file.file, encoding='utf-8'))
        batch = []
        batch_size = 100
        inserted = 0
        for row in reader:
            batch.append((
                row.get('name'),
                row.get('description'),
                float(row.get('price', 0)),
                int(row.get('in_stock', 0)),
            ))
            if len(batch) >= batch_size:
                cur.executemany(
                    "INSERT INTO product (name, description, price, in_stock) VALUES (%s, %s, %s, %s)",
                    batch
                )
                conn.commit()
                inserted += len(batch)
                batch.clear()
        if batch:
            cur.executemany(
                "INSERT INTO product (name, description, price, in_stock) VALUES (%s, %s, %s, %s)",
                batch
            )
            conn.commit()
            inserted += len(batch)
        return {"inserted": inserted}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

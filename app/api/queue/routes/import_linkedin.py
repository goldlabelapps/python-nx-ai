import os
import csv
import time
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.post("/queue/import/linkedin")
def import_linkedin_csv() -> dict:
    """POST /queue/import/linkedin: Import data from linkedin_sample.csv into the queue table."""
    csv_path = os.path.join(os.path.dirname(__file__), "../csv/linkedin/linkedin_sample.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="linkedin_sample.csv not found")
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(row for row in csvfile if not row.startswith('Notes:'))
            now = int(time.time())
            for row in reader:
                cursor.execute(
                    """
                    INSERT INTO queue (first_name, last_name, url, email_address, company, position, connected_on, created, updated, hidden, collection)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        row.get('First Name'),
                        row.get('Last Name'),
                        row.get('URL'),
                        row.get('Email Address'),
                        row.get('Company'),
                        row.get('Position'),
                        row.get('Connected On'),
                        now,
                        now,
                        False,
                        'prospects'
                    ]
                )
        conn.commit()
        conn.close()
        return {"meta": make_meta("success", "LinkedIn CSV imported")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

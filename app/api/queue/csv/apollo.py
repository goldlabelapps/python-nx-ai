import os
import csv
import time
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.post("/queue/csv/apollo")
def import_apollo_csv() -> dict:
    """POST /queue/csv/apollo: Import data from apollo.csv into the queue table (template)."""
    csv_path = os.path.join(os.path.dirname(__file__), "../csv/apollo/apollo-3.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="csv not found")
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            now = int(time.time())
            batch = []
            batch_size = 500
            imported_count = 0
            for row in reader:
                if not any(row.values()):
                    continue
                batch.append([
                    now,  # updated
                    False,  # hidden
                    now,  # created
                    row.get('Email', ''),  # email
                    row.get('Company Name', ''),  # company
                    row.get('Title', ''),  # job
                    row.get('Person Linkedin Url', ''),  # linkedin
                    row.get('First Name', ''),  # first_name
                    row.get('Last Name', ''),  # last_name
                    row.get('Seniority', None),  # seniority
                    row.get('Sub Departments', None),  # department
                    row.get('Corporate Phone', None),  # phone
                    row.get('Country', None),  # country
                    None,  # connected (not present, set None)
                    'apollo',  # collection
                    'magento'  # group
                ])
                imported_count += 1
                if len(batch) >= batch_size:
                    cursor.executemany(
                        '''INSERT INTO queue (
                            updated, hidden, created, email, company, job, linkedin, first_name, last_name, seniority, department, phone, country, connected, collection, "group"
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )''',
                        batch
                    )
                    batch = []
            if batch:
                cursor.executemany(
                    '''INSERT INTO queue (
                        updated, hidden, created, email, company, job, linkedin, first_name, last_name, seniority, department, phone, country, connected, collection, "group"
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )''',
                    batch
                )
        conn.commit()
        conn.close()
        return {"meta": make_meta("success", f"Apollo CSV imported: {imported_count} records imported"), "imported": imported_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

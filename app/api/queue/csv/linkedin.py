import os
import csv
import time
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.post("/queue/csv/linkedin")
def import_linkedin_csv() -> dict:
    """POST /queue/csv/linkedin: Import data from linkedin.csv into the queue table, robust for large files."""
    csv_path = os.path.join(os.path.dirname(__file__), "../csv/linkedin/linkedin_sample.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="linkedin.csv not found")
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            header_line = None
            pre_data_lines = []
            while True:
                pos = csvfile.tell()
                line = csvfile.readline()
                if not line:
                    break
                if line.strip().startswith("First Name,Last Name,URL,Email Address,Company,Job,Connected On") or \
                   line.strip().startswith("First Name,Last Name,URL,Email Address,Company,Position,Connected On"):
                    header_line = line.strip()
                    break
                pre_data_lines.append(line)
            if not header_line:
                raise HTTPException(status_code=400, detail="CSV header not found.")
            
            fieldnames = header_line.split(",")
            # Map 'Position' to 'Job' for backward compatibility
            fieldnames = [fn if fn != 'Position' else 'Job' for fn in fieldnames]
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            now = int(time.time())
            batch = []
            batch_size = 500
            first_row = None
            imported_count = 0
            for row in reader:
            
                if not any(row.values()):
                    continue
                if first_row is None:
                    first_row = row.copy()
                    print("DEBUG: First parsed row from CSV:", first_row)
                batch.append([
                        now,                                  # updated
                        False,                                # hidden
                        now,                                  # created
                        row.get('Email Address'),             # email
                        row.get('Company'),                   # company
                        row.get('Job') or row.get('Position'),# job (support both)
                        row.get('Connected On'),              # connected
                        'prospects',                          # collection
                        'linkedin',                           # group
                        row.get('First Name'),                # first_name
                        row.get('Last Name'),                 # last_name
                        row.get('URL')                        # linkedin
                    ])
                imported_count += 1
                if len(batch) >= batch_size:
                    cursor.executemany(
                        '''INSERT INTO queue (updated, hidden, created, email, company, job, connected, collection, "group", first_name, last_name, linkedin)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        batch
                    )
                    batch = []
            if batch:
                cursor.executemany(
                    '''INSERT INTO queue (updated, hidden, created, email, company, job, connected, collection, "group", first_name, last_name, linkedin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    batch
                )
        conn.commit()
        conn.close()
        return {"meta": make_meta("success", f"LinkedIn CSV imported (batched): {imported_count} records imported"), "imported": imported_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

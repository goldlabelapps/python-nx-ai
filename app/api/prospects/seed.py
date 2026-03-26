from app import __version__
import os, time
import csv
from fastapi import APIRouter, status
from app.utils.db import get_db_connection

router = APIRouter()

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/seed.csv'))

def normalize_column(col):
    import re
    col = col.strip().lower().replace(' ', '_')
    col = re.sub(r'[^a-z0-9_]', '', col)
    if col and col[0].isdigit():
        col = '_' + col
    return col

@router.get("/prospects/seed", status_code=status.HTTP_200_OK)
def seed_prospects() -> dict:
    """Delete and recreate the prospects table, then seed with CSV data."""
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()

    # Provided CSV data
    csv_data = '''First Name,Last Name,Title,Company Name,Email,Email Status,Primary Email Source,Primary Email Verification Source,Email Confidence,Primary Email Catch-all Status,Primary Email Last Verified At,Seniority,Sub Departments,Work Direct Phone,Home Phone,Mobile Phone,Corporate Phone,Other Phone,Do Not Call,Lists,Person Linkedin Url,Country,Subsidiary of,Subsidiary of (Organization ID),Secondary Email,Secondary Email Source,Secondary Email Status,Secondary Email Verification Source,Tertiary Email,Tertiary Email Source,Tertiary Email Status,Tertiary Email Verification Source,Primary Intent Topic,Primary Intent Score,Secondary Intent Topic,Secondary Intent Score,Qualify Contact,Cleaned\nLaurence,Brophy,Finance Director,Abraham Moon & Sons,laurence.brophy@moons.co.uk,Verified,Apollo,Apollo,,,2026-03-18T22:36:33+00:00,Director,Finance,,,,'+44 194 387 3181,,FALSE,Magento 2,http://www.linkedin.com/in/laurence-brophy-248752145,United Kingdom,,,,,,,,,,,,,,,,\nJulie,Lavington,CEO and Founder,Sosandar,julie.lavington@sosandar.com,Verified,Apollo,Apollo,,,2026-03-11T10:33:18+00:00,Founder,"Executive, Founder",,,,'+44 333 305 2866,,FALSE,Magento 2,http://www.linkedin.com/in/julie-lavington-1181744,United Kingdom,,,,,,,,,,,,,,,,\nAndrew,Shand,Chief Executive Officer,Ruroc,andrew.shand@ruroc.com,Verified,Apollo,Apollo,,,2026-03-16T21:14:58+00:00,C suite,Executive,,,,,,FALSE,Magento 2,http://www.linkedin.com/in/andrew-shand-74068513,United Kingdom,,,,,,,,,,,,,,,,\nNick,Anstee,Head of Server Support / Programmer,Stock in the Channel,nick.anstee@stockinthechannel.com,Verified,Apollo,Apollo,,Not Catch-all,2026-03-24T09:59:02+00:00,Head,"Software Development, Support / Technical Services, Application Development, Servers",,,,'+44 845 225 2125,,FALSE,Magento 2,http://www.linkedin.com/in/nick-anstee-4b102277,United Kingdom,,,,,,,,,,,,,,,,'''

    import io
    reader = csv.reader(io.StringIO(csv_data))
    columns_raw = next(reader)
    columns = [normalize_column(col) for col in columns_raw]

    # Drop and recreate table
    cur.execute('DROP TABLE IF EXISTS prospects;')
    create_cols = ',\n    '.join([f'{col} TEXT' for col in columns])
    cur.execute(f'''CREATE TABLE prospects (\n    id SERIAL PRIMARY KEY,\n    {create_cols}\n);''')

    # Insert rows
    for row in reader:
        placeholders = ', '.join(['%s'] * len(columns))
        cur.execute(
            f"INSERT INTO prospects ({', '.join(columns)}) VALUES ({placeholders})",
            row
        )

    conn.commit()
    cur.execute('SELECT * FROM prospects;')
    if cur.description is None:
        prospects = []
    else:
        colnames = [desc[0] for desc in cur.description]
        prospects = [dict(zip(colnames, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    epoch = int(time.time() * 1000)
    meta = {
        "severity": "success",
        "title": "Prospects table seeded",
        "version": __version__,
        "base_url": base_url,
        "time": epoch,
    }
    return {"meta": meta, "data": prospects}

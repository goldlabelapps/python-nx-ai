from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter
from app.utils.db import get_db_connection

router = APIRouter()
    
base_url = os.getenv("BASE_URL", "http://localhost:8000")

@router.get("/prospects")
def root() -> dict:
    """GET /prospects endpoint."""
    meta = make_meta("success", "Prospects placeholder")
    data = {"init": f"{base_url}/prospects/init"}
    return {"meta": meta, "data": data}

# endpoint: /prospects/init
@router.get("/prospects/init")
def prospects_init() -> dict:
    """Initialize prospects and return real total count."""
    meta = make_meta("success", "Init prospects")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    title = []
    total_unique_title = 0
    seniority = []
    total_unique_seniority = 0
    sub_departments = []
    total_unique_sub_departments = 0
    try:
        cur.execute('SELECT COUNT(*) FROM prospects;')
        row = cur.fetchone()
        total = row[0] if row is not None else 0

        # Get unique titles and their counts (column is 'title')
        cur.execute('SELECT title, COUNT(*) FROM prospects WHERE title IS NOT NULL GROUP BY title ORDER BY COUNT(*) DESC;')
        title_rows = cur.fetchall()
        def slugify(text):
            import re
            text = str(text).lower()
            text = re.sub(r'[^a-z0-9]+', '-', text)
            return text.strip('-')

        title = [
            {"label": str(t[0]), "value": slugify(t[0])}
            for t in title_rows
            if t[0] is not None and str(t[0]).strip() != "" and slugify(t[0]) != ""
        ]
        total_unique_title = len(title)

        # Get unique seniority and their counts (column is 'seniority')
        cur.execute('SELECT seniority, COUNT(*) FROM prospects WHERE seniority IS NOT NULL GROUP BY seniority ORDER BY COUNT(*) DESC;')
        seniority_rows = cur.fetchall()
        seniority = [
            {"label": str(s[0]), "value": slugify(s[0])}
            for s in seniority_rows
            if s[0] is not None and str(s[0]).strip() != "" and slugify(s[0]) != ""
        ]
        total_unique_seniority = len(seniority)

        # Get unique sub_departments and their counts (column is 'sub_departments')
        cur.execute('SELECT sub_departments, COUNT(*) FROM prospects WHERE sub_departments IS NOT NULL GROUP BY sub_departments ORDER BY COUNT(*) DESC;')
        sub_department_rows = cur.fetchall()
        sub_departments = [
            {"label": str(sd[0]), "value": slugify(sd[0])}
            for sd in sub_department_rows
            if sd[0] is not None and str(sd[0]).strip() != "" and slugify(sd[0]) != ""
        ]
        total_unique_sub_departments = len(sub_departments)
    except Exception:
        total = 0
        title = []
        total_unique_title = 0
        seniority = []
        total_unique_seniority = 0
        sub_departments = []
        total_unique_sub_departments = 0
    finally:
        cur.close()
        conn.close()
    data = {
        "total": total,
        "groups": { 
            "level": {
                "total": total_unique_seniority,
                "list": seniority
            },
            "job": {
                "total": total_unique_title,
                "list": title
            },
            "lane": {
                "total": total_unique_sub_departments,
                "list": sub_departments
            }
        },
    }
    return {"meta": meta, "data": data}

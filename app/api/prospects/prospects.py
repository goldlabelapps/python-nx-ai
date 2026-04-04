
from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path, Body, HTTPException
from app.utils.db import get_db_connection

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")


# Refactored GET /prospects endpoint to return paginated, filtered, and ordered results
@router.get("/prospects")
def get_prospects(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(50, ge=1, le=500, description="Records per page (default 50, max 500)")
) -> dict:
    """Return paginated, filtered, and ordered prospects (flagged first, then alphabetical by first_name)."""
    meta = make_meta("success", "Read paginated prospects")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    offset = (page - 1) * limit
    try:
        cur.execute('SELECT COUNT(*) FROM prospects WHERE hide IS NOT TRUE;')
        count_row = cur.fetchone() if cur.description is not None else None
        total = count_row[0] if count_row is not None else 0
        # Order: flagged first (flag DESC NULLS LAST), then first_name ASC
        cur.execute('''
            SELECT * FROM prospects
            WHERE hide IS NOT TRUE
            ORDER BY COALESCE(flag, FALSE) DESC, first_name ASC
            OFFSET %s LIMIT %s;
        ''', (offset, limit))
        if cur.description is not None:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
        else:
            data = []
    except Exception as e:
        data = []
        total = 0
        meta = make_meta("error", f"Failed to read prospects: {str(e)}")
    finally:
        cur.close()
        conn.close()
    return {
        "meta": meta,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total // limit) + (1 if total % limit else 0)
        },
        "data": data,
    }




# Schema for update
from pydantic import BaseModel
from typing import Optional

class ProspectUpdate(BaseModel):
    flag: Optional[bool] = None
    hide: Optional[bool] = None


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
        cur.execute('SELECT COUNT(*) FROM prospects WHERE hide IS NOT TRUE;')
        row = cur.fetchone()
        total = row[0] if row is not None else 0

        # Get unique titles and their counts (column is 'title')
        cur.execute('SELECT title, COUNT(*) FROM prospects WHERE title IS NOT NULL AND hide IS NOT TRUE GROUP BY title ORDER BY COUNT(*) DESC;')
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
        cur.execute('SELECT seniority, COUNT(*) FROM prospects WHERE seniority IS NOT NULL AND hide IS NOT TRUE GROUP BY seniority ORDER BY COUNT(*) DESC;')
        seniority_rows = cur.fetchall()
        seniority = [
            {"label": str(s[0]), "value": slugify(s[0])}
            for s in seniority_rows
            if s[0] is not None and str(s[0]).strip() != "" and slugify(s[0]) != ""
        ]
        total_unique_seniority = len(seniority)

        # Get unique sub_departments and their counts (column is 'sub_departments')
        cur.execute('SELECT sub_departments, COUNT(*) FROM prospects WHERE sub_departments IS NOT NULL AND hide IS NOT TRUE GROUP BY sub_departments ORDER BY COUNT(*) DESC;')
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
            "seniority": {
                "total": total_unique_seniority,
                "list": seniority
            },
            "title": {
                "total": total_unique_title,
                "list": title
            },
            "sub_departments": {
                "total": total_unique_sub_departments,
                "list": sub_departments
            }
        },
        "message": "This is a placeholder for prospects/init."
    }
    return {"meta": meta, "data": data}


# endpoint: /prospects/{id}
# endpoint: /prospects/{id}
@router.get("/prospects/{id}")
def prospects_read_one(id: int = Path(..., description="ID of the prospect to retrieve")) -> dict:
    """Read and return a single prospect document by id, unless hidden."""
    meta = make_meta("success", f"Read prospect with id {id}")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM prospects WHERE id = %s AND hide IS NOT TRUE;', (id,))
        if cur.description is not None:
            row = cur.fetchone()
            if row is not None:
                columns = [desc[0] for desc in cur.description]
                data = dict(zip(columns, row))
            else:
                data = None
                meta = make_meta("error", f"No prospect found with id {id}")
        else:
            data = None
            meta = make_meta("error", f"No prospect found with id {id}")
    except Exception as e:
        data = None
        meta = make_meta("error", f"Failed to read prospect: {str(e)}")
    finally:
        cur.close()
        conn.close()
    return {"meta": meta, "data": data}


# PATCH endpoint to update flag/hide
@router.patch("/prospects/{id}")
def update_prospect(id: int = Path(..., description="ID of the prospect to update"), update: ProspectUpdate = Body(...)) -> dict:
    """Update flag and/or hide fields for a prospect by id."""
    meta = make_meta("success", f"Updated prospect with id {id}")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    fields = []
    values = []
    if update.flag is not None:
        fields.append("flag = %s")
        values.append(update.flag)
    if update.hide is not None:
        fields.append("hide = %s")
        values.append(update.hide)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update.")
    values.append(id)
    try:
        cur.execute(f"UPDATE prospects SET {', '.join(fields)} WHERE id = %s RETURNING *;", tuple(values))
        if cur.description is not None:
            row = cur.fetchone()
            if row is not None:
                columns = [desc[0] for desc in cur.description]
                data = dict(zip(columns, row))
            else:
                data = None
                meta = make_meta("error", f"No prospect found with id {id}")
        else:
            data = None
            meta = make_meta("error", f"No prospect found with id {id}")
        conn.commit()
    except Exception as e:
        data = None
        meta = make_meta("error", f"Failed to update prospect: {str(e)}")
    finally:
        cur.close()
        conn.close()
    return {"meta": meta, "data": data}
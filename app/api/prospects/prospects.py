
from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path
from app.utils.db import get_db_connection

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")

@router.get("/prospects")
def root() -> dict:
    """GET /prospects endpoint."""
    meta = make_meta("success", "Prospects endpoint")
    data = [
        {"init": f"{base_url}/prospects/init"},
        {"search": f"{base_url}/prospects/search/?query=karen"},
    ]
    return {"meta": meta, "data": data}

# endpoint: /prospects/read
@router.get("/prospects/read")
def prospects_read(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(50, ge=1, le=500, description="Records per page (default 50, max 500)")
) -> dict:
    """Read and return paginated rows from the prospects table."""
    meta = make_meta("success", "Read paginated prospects")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    offset = (page - 1) * limit
    try:
        cur.execute('SELECT COUNT(*) FROM prospects;')
        count_row = cur.fetchone() if cur.description is not None else None
        total = count_row[0] if count_row is not None else 0
        cur.execute(f'SELECT * FROM prospects OFFSET %s LIMIT %s;', (offset, limit))
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

from typing import Optional

# endpoint: /prospects/search
@router.get("/prospects/search")
def prospects_search(query: Optional[str] = Query(None, description="Search query string"),
                    page: int = Query(1, ge=1, description="Page number (1-based)"),
                    limit: int = Query(50, ge=1, le=500, description="Records per page (default 50, max 500)")) -> dict:
    """Search prospects using full-text search on search_vector column."""
    meta = make_meta("success", f"Search prospects for query: {query}")
    data = []
    total = 0
    if not query or not query.strip():
        meta = make_meta("error", "Query parameter is required for search.")
        return {"meta": meta, "data": [], "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0}}
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    offset = (page - 1) * limit
    try:
        # Count total matches
        cur.execute("SELECT COUNT(*) FROM prospects WHERE search_vector @@ plainto_tsquery('english', %s);", (query,))
        count_row = cur.fetchone() if cur.description is not None else None
        total = count_row[0] if count_row is not None else 0
        # Fetch paginated results
        cur.execute("SELECT * FROM prospects WHERE search_vector @@ plainto_tsquery('english', %s) OFFSET %s LIMIT %s;", (query, offset, limit))
        if cur.description is not None:
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
        else:
            data = []
    except Exception as e:
        meta = make_meta("error", f"Search failed: {str(e)}")
        data = []
        total = 0
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
        "message": "This is a placeholder for prospects/init."
    }
    return {"meta": meta, "data": data}


# endpoint: /prospects/{id}
@router.get("/prospects/{id}")
def prospects_read_one(id: int = Path(..., description="ID of the prospect to retrieve")) -> dict:
    """Read and return a single prospect document by id."""
    meta = make_meta("success", f"Read prospect with id {id}")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM prospects WHERE id = %s;', (id,))
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
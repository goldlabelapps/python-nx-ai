from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path, Body, HTTPException
from app.utils.db import get_db_connection

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")


# Refactored GET /prospects endpoint to return paginated, filtered, and ordered results
@router.get("/prospects/flagged")
def get_prospects(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(50, ge=1, le=500, description="Records per page (default 50, max 500)"),
    search: str = Query(None, description="Search term for first or last name (case-insensitive, partial match)")
) -> dict:
    """Return flagged prospects, filtered by search if provided."""
    meta = make_meta("success", "Flagged prospects")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    offset = (page - 1) * limit
    try:
        where_clauses = ["hide IS NOT TRUE", "flag IS TRUE"]
        params = []
        if search:
            where_clauses.append("(LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s)")
            search_param = f"%{search.lower()}%"
            params.extend([search_param, search_param])
        where_sql = " AND ".join(where_clauses)

        # Count query
        count_query = f'SELECT COUNT(*) FROM prospects WHERE {where_sql};'
        cur.execute(count_query, params)
        count_row = cur.fetchone() if cur.description is not None else None
        total = count_row[0] if count_row is not None else 0

        # Data query
        data_query = f'''
            SELECT * FROM prospects
            WHERE {where_sql}
            ORDER BY first_name ASC
            OFFSET %s LIMIT %s;
        '''
        cur.execute(data_query, params + [offset, limit])
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
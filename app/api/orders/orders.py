from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path, Body, HTTPException
from app.utils.db import get_db_connection

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")




# Refactored GET /orders endpoint to return paginated, filtered, and ordered results
@router.get("/orders")
def get_orders(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(100, ge=1, le=500, description="Records per page (default 100, max 500)"),
    search: str = Query(None, description="Search string (case-insensitive, partial match)"),
    hideflagged: bool = Query(False, description="If true, flagged records are excluded")
) -> dict:
    """Return paginated, filtered, and ordered records, filtered by search if provided."""
    meta = make_meta("success", "Read paginated orders")
    conn_gen = get_db_connection()
    conn = next(conn_gen)
    cur = conn.cursor()
    offset = (page - 1) * limit
    try:
        # Build WHERE clause
        where_clauses = ["hide IS NOT TRUE"]
        params = []
        if hideflagged:
            where_clauses.append("flag IS NOT TRUE")
        # No first_name/last_name search, as those columns do not exist
        where_sql = " AND ".join(where_clauses)

        # Count query
        count_query = f'SELECT COUNT(*) FROM orders WHERE {where_sql};'
        cur.execute(count_query, params)
        count_row = cur.fetchone() if cur.description is not None else None
        total = count_row[0] if count_row is not None else 0

        # Data query
        data_query = f'''
            SELECT * FROM orders
            WHERE {where_sql}
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
        meta = make_meta("error", f"Failed to read orders: {str(e)}")
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


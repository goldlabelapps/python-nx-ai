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
    limit: int = Query(100, ge=1, le=500, description="Records per page (default 100, max 500)"),
    search: str = Query(None, description="Search term for first or last name (case-insensitive, partial match)"),
    hideflagged: bool = Query(False, description="If true, flagged records are excluded")
) -> dict:
    """Return paginated, filtered, and ordered prospects (then alphabetical by first_name), filtered by search if provided."""
    meta = make_meta("success", "Read paginated prospects")
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




# Schema for update
from pydantic import BaseModel
from typing import Optional

class ProspectUpdate(BaseModel):
    flag: Optional[bool] = None
    hide: Optional[bool] = None

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
                # Fetch related llm records
                try:
                    from app.utils.db import get_db_connection_direct
                    llm_conn = get_db_connection_direct()
                    llm_cur = llm_conn.cursor()
                    llm_cur.execute("SELECT id, prompt, completion, duration, time, data, model FROM llm WHERE prospect_id = %s ORDER BY id DESC;", (id,))
                    llm_records = [
                        {
                            "id": r[0],
                            "prompt": r[1],
                            "completion": r[2],
                            "duration": r[3],
                            "time": r[4].isoformat() if r[4] else None,
                            "data": r[5],
                            "model": r[6],
                        }
                        for r in llm_cur.fetchall()
                    ]
                    llm_cur.close()
                    llm_conn.close()
                    data["llm_records"] = llm_records
                except Exception as llm_exc:
                    data["llm_records"] = []
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
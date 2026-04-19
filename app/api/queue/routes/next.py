import os
from fastapi import APIRouter, HTTPException, Query
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()


# Route: /queue/next?collection=prospects&group=linkedin
@router.get("/queue/next")
def get_next_queue(
    collection: str = Query(None, description="Filter by collection name"),
    group: str = Query(None, description="Filter by group name")
) -> dict:
    """Return the next queue record filtered by collection/group, ordered by latest updated."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()

        # Build query with optional filters
        query = "SELECT * FROM queue"
        filters = []
        params = []
        if collection:
            filters.append("collection = %s")
            params.append(collection)
        if group:
            filters.append('"group" = %s')
            params.append(group)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY updated DESC LIMIT 1;"

        cursor.execute(query, params)
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        if row and columns:
            record = dict(zip(columns, row))
            # Build a dynamic title with filters
            filters = []
            if collection:
                filters.append(f"collection='{collection}'")
            if group:
                filters.append(f"group='{group}'")
            filter_str = f" (filtered by {', '.join(filters)})" if filters else ""
            title = f"Next queue record found{filter_str}"
            return {
                "meta": make_meta("success", title),
                "data": record
            }
        else:
            return {
                "meta": make_meta("info", "No queue record to show"),
                "data": None,
                "message": "Nothing to show for the given filters."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

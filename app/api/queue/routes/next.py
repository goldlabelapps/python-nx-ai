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
        base_query = "SELECT * FROM queue"
        filters = []
        params = []
        if collection:
            filters.append("collection = %s")
            params.append(collection)
        if group:
            filters.append('"group" = %s')
            params.append(group)
        where_clause = (" WHERE " + " AND ".join(filters)) if filters else ""

        # 1. Get the next record
        query = base_query + where_clause + " ORDER BY updated DESC LIMIT 1;"
        cursor.execute(query, params)
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        record = dict(zip(columns, row)) if row and columns else None

        # 2. Get count of records matching filters
        count_query = "SELECT COUNT(*) FROM queue" + where_clause + ";"
        cursor.execute(count_query, params)
        filtered_row = cursor.fetchone()
        filtered_count = filtered_row[0] if filtered_row else 0

        # 3. Get total count
        cursor.execute("SELECT COUNT(*) FROM queue;")
        total_row = cursor.fetchone()
        total_count = total_row[0] if total_row else 0

        # 4. Get table schema
        cursor.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'queue';")
        schema = [
            {"name": row[0], "type": row[1], "nullable": row[2]} for row in cursor.fetchall()
        ]

        conn.close()

        # Build a dynamic title with filters
        filter_labels = []
        if collection:
            filter_labels.append(f"collection='{collection}'")
        if group:
            filter_labels.append(f"group='{group}'")
        filter_str = f" (filtered by {', '.join(filter_labels)})" if filter_labels else ""
        title = f"Next queue record found{filter_str}" if record else "No queue record to show"

        return {
            "meta": make_meta("success" if record else "info", title),
            "data": {
                "record": record,
                "filtered_count": filtered_count,
                "total_count": total_count,
                "schema": schema,
                "message": None if record else "Nothing to show for the given filters."
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

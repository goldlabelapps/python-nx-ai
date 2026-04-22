import os
from fastapi import APIRouter, HTTPException, Query
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct

router = APIRouter()

@router.get("/queue")
def read_queue(
    collection: str = Query(None, description="Filter by collection name"),
    group: str = Query(None, description="Filter by group name")
) -> dict:
    """GET /queue: Return queue table info, schema, and most recent record."""
    try:
        conn = get_db_connection_direct()
        cursor = conn.cursor()

        # 1. Total record count (unfiltered)
        cursor.execute("SELECT COUNT(*) FROM queue;")
        count_row = cursor.fetchone()
        total_count = count_row[0] if count_row else 0

        # 2. Get unique values from collection and group columns
        cursor.execute("SELECT DISTINCT collection FROM queue WHERE collection IS NOT NULL;")
        collections = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT "group" FROM queue WHERE "group" IS NOT NULL;')
        groups = [row[0] for row in cursor.fetchall()]

        # 3. Build filter conditions
        filters = []
        params = []
        if collection:
            filters.append("collection = %s")
            params.append(collection)
        if group:
            filters.append('"group" = %s')
            params.append(group)
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        # 4. Filtered count
        count_query = f"SELECT COUNT(*) FROM queue {where_clause};"
        cursor.execute(count_query, params)
        filtered_count_row = cursor.fetchone()
        filtered_count = filtered_count_row[0] if filtered_count_row else 0

        # 5. Get the next in queue (most recently updated in filtered list)
        next_query = f"SELECT * FROM queue {where_clause} ORDER BY updated DESC LIMIT 1;"
        cursor.execute(next_query, params)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        row = cursor.fetchone()
        next_record = dict(zip(columns, row)) if row and columns else None

        conn.close()

        return {
            "meta": make_meta("success", "Queue table info"),
            "data": {
                "total": total_count,
                "filtered": filtered_count,
                "filters": {
                    "collectionFilter": collection,
                    "groupFilter": group,
                    "collections": collections,
                    "groups": groups,
                },
                "next": next_record,
            }
        }
    except Exception as e:
        return {
            "meta": make_meta("error", str(e)),
            "data": None
        }

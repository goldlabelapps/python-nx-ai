import os
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.get("/llm")
def get_llm_records(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Records per page")
    , api_key: str = Depends(get_api_key)
) -> dict:
    """GET /llm: Paginated list of LLM completions."""
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        offset = (page - 1) * page_size
        cur.execute("SELECT COUNT(*) FROM llm;")
        count_row = cur.fetchone()
        total = count_row[0] if count_row and count_row[0] is not None else 0
        cur.execute("""
            SELECT id, prompt, completion, duration, time, data, model, prospect_id
            FROM llm
            ORDER BY id DESC
            LIMIT %s OFFSET %s;
        """, (page_size, offset))
        records = [
            {
                "id": row[0],
                "prompt": row[1],
                "completion": row[2],
                "duration": row[3],
                "time": row[4].isoformat() if row[4] else None,
                "data": row[5],
                "model": row[6],
                "prospect_id": row[7],
            }
            for row in cur.fetchall()
        ]
        cur.close()
        conn.close()
        meta = make_meta("success", f"LLM {len(records)} records (page {page})")
        return {
            "meta": meta,
            "data": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size,
                "data": records,
            },
        }
    except Exception as e:
        meta = make_meta("error", f"DB error: {str(e)}")
        return {"meta": meta, "data": {}}

@router.post("/llm")
def llm_post(payload: dict) -> dict:
    """POST /llm: send prompt to Gemini, returns completion google-genai SDK."""
    prompt = payload.get("prompt")
    prospect_id = payload.get("prospect_id")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
    import logging
    try:
        from google import genai
        import time as time_mod
        client = genai.Client(api_key=api_key)
        model_names = [
            "models/gemini-flash-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.0-pro",
            "models/gemini-pro",
            "models/gemini-pro-vision"
        ]
        response = None
        completion = None
        used_model = None
        errors = {}
        start_time = time_mod.time()
        for model_name in model_names:
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                completion = getattr(response, "text", None)
                if completion:
                    used_model = model_name
                    break
            except Exception as e:
                errors[model_name] = str(e)
                continue
        duration = time_mod.time() - start_time
        if not completion:
            error_details = " | ".join([f"{k}: {v}" for k, v in errors.items()])
            raise Exception(f"No available Gemini model succeeded for generate_content with your API key. Details: {error_details}")
        # Insert record into llm table
        record_id = None
        try:
            import json
            from app import __version__
            data_blob = json.dumps({"version": __version__})
            conn = get_db_connection_direct()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO llm (prompt, completion, duration, data, model, prospect_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (prompt, completion, duration, data_blob, used_model, prospect_id)
            )
            record_id_row = cur.fetchone()
            record_id = record_id_row[0] if record_id_row else None
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_exc:
            # Log DB error but do not fail the API response
            logging.error(f"Failed to insert llm record: {db_exc}")
        meta = make_meta("success", f"Gemini completion received from {used_model}")
        return {"meta": meta, "data": {"id": record_id, "prompt": prompt, "completion": completion}}
    except Exception as e:
        meta = make_meta("error", f"Gemini API error: {str(e)}")
        return {"meta": meta, "data": {}}
    

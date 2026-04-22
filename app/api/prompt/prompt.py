import os
from fastapi import APIRouter, HTTPException, Depends
from app.utils.make_meta import make_meta
from app.utils.db import get_db_connection_direct
from app.utils.api_key_auth import get_api_key

router = APIRouter()

@router.get("/prompt")
@router.get("/prompts")
def get_prompt_table_metadata(api_key: str = Depends(get_api_key)) -> dict:
    """GET /prompt: Return prompt table metadata."""
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM prompt;")
        count_row = cur.fetchone()
        record_count = count_row[0] if count_row and count_row[0] is not None else 0
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'prompt'
            ORDER BY ordinal_position;
            """
        )
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        meta = make_meta("success", "Prompt table metadata")
        return {
            "meta": meta,
            "data": {
                "record_count": record_count,
                "columns": columns,
            },
        }
    except Exception as e:
        meta = make_meta("error", f"DB error: {str(e)}")
        return {"meta": meta, "data": {}}

@router.post("/prompt")
def llm_post(payload: dict) -> dict:
    """POST /prompt: send prompt to Gemini, returns completion google-genai SDK."""
    prompt = payload.get("prompt")
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
        # Insert record into prompt table
        record_id = None
        try:
            import json
            from app import __version__
            data_blob = json.dumps({"version": __version__})
            conn = get_db_connection_direct()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO prompt (prompt, completion, duration, data, model)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (prompt, completion, duration, data_blob, used_model)
            )
            record_id_row = cur.fetchone()
            record_id = record_id_row[0] if record_id_row else None
            conn.commit()
            cur.close()
            conn.close()
        except Exception as db_exc:
            # Log DB error but do not fail the API response
            logging.error(f"Failed to insert prompt record: {db_exc}")
        meta = make_meta("success", f"Gemini completion received from {used_model}")
        return {"meta": meta, "data": {"id": record_id, "prompt": prompt, "completion": completion}}
    except Exception as e:
        meta = make_meta("error", f"Gemini API error: {str(e)}")
        return {"meta": meta, "data": {}}
    

import os
import hashlib
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
        cur.execute(
            """
            SELECT id, prompt, completion, time, model
            FROM prompt
            ORDER BY id DESC
            LIMIT 1;
            """
        )
        top_row = cur.fetchone()
        cur.close()
        conn.close()
        meta = make_meta("success", "Prompt table metadata")
        return {
            "meta": meta,
            "data": {
                "first_record": {
                    "id": top_row[0],
                    # "prompt": top_row[1],
                    # "completion": top_row[2],
                    "time": top_row[3].isoformat() if top_row and top_row[3] else None,
                    "model": top_row[4],
                } if top_row else None,
                "record_count": record_count,
                "columns": columns,
            },
        }
    except Exception as e:
        meta = make_meta("error", f"DB error: {str(e)}")
        return {"meta": meta, "data": {}}

@router.post("/prompt")
def llm_post(payload: dict) -> dict:
    """POST /prompt: send prompt to Gemini with DB-backed caching."""
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    conn = None
    cur = None
    import logging
    try:
        conn = get_db_connection_direct()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'prompt'
                  AND column_name = 'search_vector'
            );
            """
        )
        exists_row = cur.fetchone()
        has_search_vector = bool(exists_row and exists_row[0])

        # Fast/safe cache hit: exact prompt hash or exact prompt text.
        cur.execute(
            """
            SELECT id, prompt, completion, time, model
            FROM prompt
            WHERE COALESCE(data->>'prompt_hash', '') = %s OR prompt = %s
            ORDER BY id DESC
            LIMIT 1;
            """,
            (prompt_hash, prompt),
        )
        row = cur.fetchone()

        # Fallback cache hit when tsvector exists and query terms match strongly.
        if not row and has_search_vector:
            cur.execute(
                """
                SELECT id, prompt, completion, time, model,
                       ts_rank_cd(search_vector, plainto_tsquery('english', %s)) AS rank
                FROM prompt
                WHERE search_vector @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC, id DESC
                LIMIT 1;
                """,
                (prompt, prompt),
            )
            rank_row = cur.fetchone()
            if rank_row and rank_row[5] is not None and float(rank_row[5]) >= 0.35:
                row = rank_row[:5]

        cur.close()
        conn.close()
        cur = None
        conn = None

        if row:
            return {
                "meta": make_meta("success", "Prompt returned from cache"),
                "data": {
                    "cached": True,
                    "prompt_id": row[0],
                    "prompt": row[1],
                    "completion": row[2],
                    "time": row[3].isoformat() if row[3] else None,
                    "model": row[4],
                },
            }

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
            record_data = {
                "version": __version__,
                "prompt_hash": prompt_hash,
            }
            data_blob = json.dumps(record_data)
            conn = get_db_connection_direct()
            cur = conn.cursor()
            if has_search_vector:
                cur.execute(
                    """
                    INSERT INTO prompt (prompt, completion, duration, data, model, search_vector)
                    VALUES (%s, %s, %s, %s, %s, to_tsvector('english', %s || ' ' || %s))
                    RETURNING id;
                    """,
                    (prompt, completion, duration, data_blob, used_model, prompt, completion)
                )
            else:
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
        return {
            "meta": meta,
            "data": {
                "cached": False,
                "id": record_id,
                "prompt": prompt,
                "completion": completion,
                "duration": duration,
                "model": used_model,
            },
        }
    except Exception as e:
        meta = make_meta("error", f"Gemini API error: {str(e)}")
        return {"meta": meta, "data": {}}
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    

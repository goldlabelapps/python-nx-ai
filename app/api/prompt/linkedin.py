import os

from fastapi import APIRouter, Depends, HTTPException

from app.utils.api_key_auth import get_api_key
from app.utils.db import get_db_connection_direct
from app.utils.make_meta import make_meta

router = APIRouter()


@router.post("/prompt/linkedin")
def linkedin_prompt_success(payload: dict, api_key: str = Depends(get_api_key)) -> dict:
    """POST /prompt/linkedin: return cached completion or create a new Gemini analysis."""
    linkedin_url = (payload.get("linkedin_url") or payload.get("linkedinUrl") or "").strip()
    if not linkedin_url:
        raise HTTPException(status_code=400, detail="Missing 'linkedin_url' in request body.")

    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        prompt = (
            "Analyse this LinkedIn profile URL and provide a concise summary of the person, "
            "their role, company, seniority, likely responsibilities, and notable signals. "
            f"LinkedIn URL: {linkedin_url}"
        )

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")

    conn = None
    cur = None
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

        if has_search_vector:
            cur.execute(
                """
                SELECT id, prompt, completion, time, model, data
                FROM prompt
                WHERE (
                    COALESCE(data->>'linkedin_url', data->>'linkedinUrl') = %s
                    OR search_vector @@ plainto_tsquery('english', %s)
                    OR prompt ILIKE %s
                )
                ORDER BY id DESC
                LIMIT 1;
                """,
                (linkedin_url, linkedin_url, f"%{linkedin_url}%"),
            )
        else:
            cur.execute(
                """
                SELECT id, prompt, completion, time, model, data
                FROM prompt
                WHERE (COALESCE(data->>'linkedin_url', data->>'linkedinUrl') = %s OR prompt ILIKE %s)
                ORDER BY id DESC
                LIMIT 1;
                """,
                (linkedin_url, f"%{linkedin_url}%"),
            )
        row = cur.fetchone()

        if row:
            cur.close()
            conn.close()
            cur = None
            conn = None
            return {
                "meta": make_meta("success", "LinkedIn URL already analysed"),
                "data": {
                    "cached": True,
                    "id": row[0],
                    "linkedin_url": linkedin_url,
                    "prompt": row[1],
                    "completion": row[2],
                    "time": row[3].isoformat() if row[3] else None,
                    "model": row[4],
                    "record_data": row[5],
                },
            }

        cur.close()
        conn.close()
        cur = None
        conn = None

        import json
        import logging
        import time as time_mod
        from app import __version__
        from google import genai

        client = genai.Client(api_key=gemini_api_key)
        model_names = [
            "models/gemini-flash-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.0-pro",
            "models/gemini-pro",
            "models/gemini-pro-vision",
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
            except Exception as model_exc:
                errors[model_name] = str(model_exc)
                continue

        duration = time_mod.time() - start_time
        if not completion:
            error_details = " | ".join([f"{name}: {message}" for name, message in errors.items()])
            raise Exception(
                "No available Gemini model succeeded for generate_content with your API key. "
                f"Details: {error_details}"
            )

        record_id = None
        record_data = {
            "version": __version__,
            "linkedin_url": linkedin_url,
        }
        try:
            conn = get_db_connection_direct()
            cur = conn.cursor()
            data_blob = json.dumps(record_data)
            if has_search_vector:
                cur.execute(
                    """
                    INSERT INTO prompt (prompt, completion, duration, model, data, search_vector)
                    VALUES (%s, %s, %s, %s, %s, to_tsvector('english', %s || ' ' || %s))
                    RETURNING id;
                    """,
                    (prompt, completion, duration, used_model, data_blob, prompt, completion)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO prompt (prompt, completion, duration, model, data)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (prompt, completion, duration, used_model, data_blob)
                )
            record_id_row = cur.fetchone()
            record_id = record_id_row[0] if record_id_row else None
            conn.commit()
            cur.close()
            conn.close()
            cur = None
            conn = None
        except Exception as db_exc:
            logging.error(f"Failed to insert prompt record: {db_exc}")

        return {
            "meta": make_meta("success", f"Gemini completion received from {used_model}"),
            "data": {
                "cached": False,
                "id": record_id,
                "linkedin_url": linkedin_url,
                "prompt": prompt,
                "completion": completion,
                "duration": duration,
                "model": used_model,
                "record_data": record_data,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "meta": make_meta("error", f"Gemini API error: {str(e)}"),
            "data": {},
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

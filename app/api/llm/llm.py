import os
from fastapi import APIRouter, HTTPException
from app.utils.make_meta import make_meta

router = APIRouter()

@router.get("/llm")
def root() -> dict:
    """GET /llm endpoint."""
    meta = make_meta("success", "LLM endpoint says hello")
    return {"meta": meta}

@router.post("/llm")
def llm_post(payload: dict) -> dict:
    """POST /llm: send prompt to Gemini, returns completion google-genai SDK."""
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not configured.")
    import logging
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        # Try a list of known Gemini model names
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
        if not completion:
            error_details = " | ".join([f"{k}: {v}" for k, v in errors.items()])
            raise Exception(f"No available Gemini model succeeded for generate_content with your API key. Details: {error_details}")
    except Exception as e:
        meta = make_meta("error", f"Gemini API error: {str(e)}")
        return {"meta": meta, "data": {}}
    meta = make_meta("success", f"Gemini completion received from {used_model}")
    return {"meta": meta, "data": {"prompt": prompt, "completion": completion}}
    

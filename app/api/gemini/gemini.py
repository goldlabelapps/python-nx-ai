from fastapi import APIRouter

router = APIRouter()

@router.get("/gemini")
def root() -> dict:
    """GET /gemini endpoint."""
    return {"message": "Welcome to the Gemini API!"}
    

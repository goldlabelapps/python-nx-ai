
from app import __version__
import os
from app.utils.make_meta import make_meta
from fastapi import APIRouter, Query, Path, Body, HTTPException
from app.utils.db import get_db_connection
from app.utils.send_email import send_email_resend

router = APIRouter()
base_url = os.getenv("BASE_URL", "http://localhost:8000")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

@router.get("/resend")
def root() -> dict:
    """GET /resend endpoint."""
    if not RESEND_API_KEY:
        meta = make_meta("error", "RESEND_API_KEY is missing from environment. Please set it in your .env file.")
        return {"meta": meta}
    meta = make_meta("success", "Resend endpoint")
    return {"meta": meta}


# POST endpoint to send email
from fastapi import status
from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    html: str
    sender: EmailStr

@router.post("/resend", status_code=status.HTTP_202_ACCEPTED)
def send_email(request: EmailRequest):
    """POST /resend endpoint to send email via Resend API."""
    if not RESEND_API_KEY:
        meta = make_meta("error", "RESEND_API_KEY missing. Please set it in your .env file.")
        return {"meta": meta}
    result = send_email_resend(
        to=request.to,
        subject=request.subject,
        html=request.html,
        sender=request.sender
    )
    if "error" in result:
        meta = make_meta("error", result["error"])
        return {"meta": meta}
    meta = make_meta("success", "Email sent successfully.")
    return {"meta": meta, "data": result}

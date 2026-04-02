# Utility to send email using Resend API
import httpx
import os

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_API_URL = "https://api.resend.com/emails"

def send_email_resend(to: str, subject: str, html: str, sender: str) -> dict:
    if not RESEND_API_KEY:
        return {"error": "Missing RESEND_API_KEY"}
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html
    }
    try:
        response = httpx.post(RESEND_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

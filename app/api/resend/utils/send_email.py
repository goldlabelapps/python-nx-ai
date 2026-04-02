# Utility to send email using Resend API
import httpx
import os

RESEND_API_URL = "https://api.resend.com/emails"

def send_email_resend(to: str, subject: str, html: str, sender: str) -> dict:
    resend_api_key = os.getenv("RESEND_API_KEY")
    if not resend_api_key:
        return {"error": "Missing RESEND_API_KEY"}
    headers = {
        "Authorization": f"Bearer {resend_api_key}",
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

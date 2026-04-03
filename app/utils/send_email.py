# Utility to send email using official Resend package
import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_email_resend(to: str, subject: str, html: str) -> dict:
    if not resend.api_key:
        return {"error": "Missing RESEND_API_KEY"}
    params: resend.Emails.SendParams = {
        "from": "NX <nx@goldlabel.pro>",
        "to": [to],
        "subject": subject,
        "html": html,
    }
    try:
        email: resend.Emails.SendResponse = resend.Emails.send(params)
        return dict(email)
    except Exception as e:
        return {"error": str(e)}

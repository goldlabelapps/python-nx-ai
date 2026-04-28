"""Goldlabel branded HTML email template."""

_LOGO_URL = "https://goldlabel.pro/goldlabelpro/png/favicon.png"

# Palette (dark theme used for the email chrome; body text stays readable on white clients)
_DARK_BG      = "#364450"
_DARK_PAPER   = "#364450"
_DARK_PRIMARY = "#ffd849"
_DARK_TEXT    = "#ffffff"
_LIGHT_BG     = "#eaf0f5"
_LIGHT_PAPER  = "#EEF7FF"
_LIGHT_TEXT   = "#000000"
_LIGHT_PRIMARY = "#364450"


def goldlabel_email(subject: str, body_html: str) -> str:
    """Return a complete HTML email string with Goldlabel branding.

    Args:
        subject:   Used as the visible heading inside the email.
        body_html: Inner HTML content placed in the message body area.

    Returns:
        A self-contained HTML string ready to pass to send_email_resend().
    """
    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light dark" />
  <meta name="supported-color-schemes" content="light dark" />
  <title>{subject}</title>
  <style>
    /* ── Reset ─────────────────────────────────────── */
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; display: block; }}

    /* ── Base ──────────────────────────────────────── */
    body {{
      margin: 0; padding: 0;
      background-color: {_LIGHT_BG};
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: {_LIGHT_TEXT};
    }}

    /* ── Dark-mode overrides ───────────────────────── */
    @media (prefers-color-scheme: dark) {{
      body, .email-wrapper {{ background-color: {_DARK_BG} !important; color: {_DARK_TEXT} !important; }}
      .email-card         {{ background-color: {_DARK_PAPER} !important; color: {_DARK_TEXT} !important; }}
      .email-header       {{ background-color: {_DARK_BG} !important; }}
      .email-footer       {{ background-color: {_DARK_BG} !important; color: {_DARK_TEXT} !important; }}
      .email-subject      {{ color: {_DARK_PRIMARY} !important; }}
      a                   {{ color: {_DARK_PRIMARY} !important; }}
    }}
  </style>
</head>
<body class="email-wrapper">
  <!-- Outer wrapper -->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background-color:{_LIGHT_BG}; padding: 32px 0;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table role="presentation" class="email-card" width="600" cellpadding="0" cellspacing="0"
               style="max-width:600px; width:100%; background-color:{_LIGHT_PAPER};
                      border-radius:8px; overflow:hidden;
                      box-shadow: 0 2px 8px rgba(0,0,0,0.10);">

          <!-- Header -->
          <tr>
            <td class="email-header" align="center"
                style="background-color:{_DARK_BG}; padding: 28px 40px;">
              <img src="{_LOGO_URL}"
                   width="48" height="48"
                   alt="Goldlabel"
                   style="width:48px; height:48px; border-radius:8px;" />
            </td>
          </tr>

          <!-- Subject banner -->
          <tr>
            <td align="left"
                style="padding: 28px 40px 0 40px;">
              <h1 class="email-subject"
                  style="margin:0; font-size:22px; font-weight:700;
                         color:{_LIGHT_PRIMARY}; line-height:1.3;">
                {subject}
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td align="left"
                style="padding: 20px 40px 32px 40px;
                       font-size:15px; line-height:1.7; color:{_LIGHT_TEXT};">
              {body_html}
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding: 0 40px;">
              <hr style="border:none; border-top:1px solid {_DARK_PRIMARY}; margin:0;" />
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="email-footer" align="center"
                style="padding: 20px 40px;
                       font-size:12px; color:#666666;">
              <a href="https://goldlabel.pro"
                 style="color:{_LIGHT_PRIMARY}; text-decoration:none;">goldlabel.pro</a>
              &nbsp;&middot;&nbsp;
              You received this email because a request was made via the NX° API.
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>
</body>
</html>"""

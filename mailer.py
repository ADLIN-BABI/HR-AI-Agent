# import os
# import smtplib
# import logging
# from email.message import EmailMessage

# # Load SMTP settings from environment (recommended for security)
# SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
# SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
# SMTP_USER = os.getenv("SMTP_USER")  # your login email
# SMTP_PASS = os.getenv("SMTP_PASS")  # app password (not your real password!)
# FROM_NAME = os.getenv("FROM_NAME", "HR Team")

# def send_interview_email(
#     to_email: str,
#     subject: str,
#     body: str,
#     from_email: str = None
# ) -> bool:
#     """Send an interview email with subject & body."""

#     if not SMTP_USER or not SMTP_PASS:
#         logging.error("SMTP_USER or SMTP_PASS not configured. Email not sent.")
#         return False

#     try:
#         msg = EmailMessage()
#         msg["Subject"] = subject
#         msg["From"] = f"{FROM_NAME} <{from_email or SMTP_USER}>"
#         msg["To"] = to_email
#         msg.set_content(body)

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USER, SMTP_PASS)
#             server.send_message(msg)

#         logging.info(f"✅ Email sent to {to_email}")
#         return True
#     except Exception as e:
#         logging.exception(f"❌ Email send failed: {e}")
#         return False


import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

# Load env when mailer is imported
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FROM_NAME = os.getenv("FROM_NAME", "HR Team")

def send_interview_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str = None
) -> bool:
    """Send an interview email with subject & body."""
    
    # Re-fetch on every call (avoids stale values)
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    if not SMTP_USER or not SMTP_PASS:
        logging.error("SMTP_USER or SMTP_PASS not configured. Email not sent.")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{from_email or SMTP_USER}>"
        msg["To"] = to_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        logging.info(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        logging.exception(f"❌ Email send failed: {e}")
        return False

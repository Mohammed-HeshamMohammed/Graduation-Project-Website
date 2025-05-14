import smtplib
from email.mime.text import MIMEText
from app.config import EMAIL_SENDER, EMAIL_PASSWORD, DOMAIN_NAME

def send_verification_email(to_email: str, token: str):
    link = f"{DOMAIN_NAME}/verify?token={token}"
    body = f"Click the link to verify your account: {link}"
    msg = MIMEText(body)
    msg["Subject"] = "Verify Your Email"
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
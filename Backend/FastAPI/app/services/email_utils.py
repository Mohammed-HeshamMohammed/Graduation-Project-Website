# app/services/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings

async def send_verification_email(email: str, token: str):
    """
    Sends an email with a verification link
    """
    # Create verification URL with token
    verification_url = f"{settings.VERIFICATION_URL}?token={token}"
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your Email Address"
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    
    # Create both plain text and HTML versions
    text_content = f"""
    Please verify your email address by clicking the link below:
    
    {verification_url}
    
    If you did not register for this account, please ignore this email.
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>Email Verification</h2>
        <p>Please verify your email address by clicking the button below:</p>
        <p>
          <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Verify Email
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{verification_url}</p>
        <p>If you did not register for this account, please ignore this email.</p>
      </body>
    </html>
    """
    
    # Attach parts
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)
    
    # For local development, just print the verification URL
    print(f"\n--- VERIFICATION EMAIL ---\nTo: {email}\nURL: {verification_url}\n--- END EMAIL ---\n")
    
    # Uncomment to actually send emails (requires valid SMTP credentials)
    """
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    """
    
    # For development, we'll just return success
    return True
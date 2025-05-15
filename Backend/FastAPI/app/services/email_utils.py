# app/services/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings
import logging
import traceback

# Configure logging for better error tracking
logger = logging.getLogger(__name__)

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
    
    # Always log the verification URL in development environment
    if settings.ENV == "development":
        logger.info(f"\n--- VERIFICATION EMAIL ---\nTo: {email}\nURL: {verification_url}\n--- END EMAIL ---\n")
        # In development, we can "pretend" we sent the email
        return True
    
    # In production, try to send the email
    try:
        # Check if SMTP credentials are configured
        if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
            logger.warning("SMTP credentials not configured properly. Email not sent.")
            if settings.ENV == "development":
                # In development, we pretend it was sent anyway
                return True
            return False
            
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
            logger.info(f"Verification email sent to {email}")
            return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        logger.error(traceback.format_exc())
        # In development, we'll consider it "sent" anyway
        if settings.ENV == "development":
            return True
        return False
      
      
async def send_password_reset_email(email: str, token: str):
    """
    Sends an email with a password reset link
    """
    # Create reset URL with token
    reset_url = f"{settings.VERIFICATION_URL.replace('/verify', '/reset-password')}?token={token}"
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Your Password"
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    
    # Create both plain text and HTML versions
    text_content = f"""
    Password Reset Request
    
    You requested to reset your password. Please click the link below to reset your password:
    
    {reset_url}
    
    This link is valid for 1 hour.
    
    If you did not request a password reset, please ignore this email.
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Please click the button below to reset your password:</p>
        <p>
          <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Reset Password
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{reset_url}</p>
        <p>This link is valid for 1 hour.</p>
        <p>If you did not request a password reset, please ignore this email.</p>
      </body>
    </html>
    """
    
    # Attach parts
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)
    
    # Always log the reset URL in development environment
    if settings.ENV == "development":
        logger.info(f"\n--- PASSWORD RESET EMAIL ---\nTo: {email}\nURL: {reset_url}\n--- END EMAIL ---\n")
        # In development, we can "pretend" we sent the email
        return True
    
    # In production, try to send the email
    try:
        # Check if SMTP credentials are configured
        if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
            logger.warning("SMTP credentials not configured properly. Email not sent.")
            if settings.ENV == "development":
                # In development, we pretend it was sent anyway
                return True
            return False
            
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
            logger.info(f"Password reset email sent to {email}")
            return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        logger.error(traceback.format_exc())
        # In development, we'll consider it "sent" anyway
        if settings.ENV == "development":
            return True
        return False
# app/services/email_utils.py
import smtplib
import logging
import traceback
from app.config import settings
from .email_template import get_email_template

# Configure logging for better error tracking
logger = logging.getLogger(__name__)

async def send_verification_email(email: str, token: str):
    """
    Sends an email with a verification link
    """
    # Create verification URL with token
    verification_url = f"{settings.VERIFICATION_URL}?token={token}"
    
    # Email content
    subject = "Verify Your Email Address"
    content = """
    <h2 style="font-size: 22px; color: #333333; margin-bottom: 20px;">Email Verification</h2>
    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        Please verify your email address by clicking the button below:
    </p>
    <p style="font-size: 14px; line-height: 1.5; margin-top: 20px;">
        If you cannot click the button, copy and paste this link into your browser:
    </p>
    <p style="font-size: 14px; line-height: 1.5; margin-bottom: 20px; color: #3366cc;">
        {verification_url}
    </p>
    <p style="font-size: 14px; line-height: 1.5;">
        If you did not register for this account, please ignore this email.
    </p>
    """.format(verification_url=verification_url)
    
    # Create email message using template
    message = get_email_template(
        subject=subject,
        content=content,
        button_text="Verify Email",
        button_url=verification_url
    )
    
    # Set recipient
    message["To"] = email
    
    # Send the email
    return await _send_email(
        email=email,
        message=message,
        log_message=f"Verification email sent to {email}",
        error_message="Failed to send verification email",
        debug_info=f"\n--- VERIFICATION EMAIL ---\nTo: {email}\nURL: {verification_url}\n--- END EMAIL ---\n"
    )
      
      
async def send_password_reset_email(email: str, token: str):
    """
    Sends an email with a password reset link
    """
    # Create reset URL with token
    reset_url = f"{settings.VERIFICATION_URL.replace('/verify', '/reset-password')}?token={token}"
    
    # Email content
    subject = "Reset Your Password"
    content = """
    <h2 style="font-size: 22px; color: #333333; margin-bottom: 20px;">Password Reset Request</h2>
    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        You requested to reset your password. Please click the button below to reset your password:
    </p>
    <p style="font-size: 14px; line-height: 1.5; margin-top: 20px;">
        If you cannot click the button, copy and paste this link into your browser:
    </p>
    <p style="font-size: 14px; line-height: 1.5; margin-bottom: 20px; color: #3366cc;">
        {reset_url}
    </p>
    <p style="font-size: 14px; line-height: 1.5;">
        This link is valid for 1 hour.
    </p>
    <p style="font-size: 14px; line-height: 1.5;">
        If you did not request a password reset, please ignore this email.
    </p>
    """.format(reset_url=reset_url)
    
    # Create email message using template
    message = get_email_template(
        subject=subject,
        content=content,
        button_text="Reset Password",
        button_url=reset_url
    )
    
    # Set recipient
    message["To"] = email
    
    # Send the email
    return await _send_email(
        email=email,
        message=message,
        log_message=f"Password reset email sent to {email}",
        error_message="Failed to send password reset email",
        debug_info=f"\n--- PASSWORD RESET EMAIL ---\nTo: {email}\nURL: {reset_url}\n--- END EMAIL ---\n"
    )


async def send_welcome_email(email: str, user_name: str):
    """
    Sends a welcome email after successful registration and verification
    """
    # Create dashboard URL
    dashboard_url = f"{settings.WEBSITE_URL}/demo-dashboard"
    
    # Email content
    subject = "Welcome to TRUCKING"
    content = """
    <h2 style="font-size: 22px; color: #333333; margin-bottom: 20px;">Welcome to TRUCKING, {user_name}!</h2>
    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        Thank you for joining our platform. Your account is now active and ready to use.
    </p>
    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        With TRUCKING, you can:
    </p>
    <ul style="font-size: 16px; line-height: 1.5; margin-bottom: 20px; padding-left: 20px;">
        <li>Manage your fleet efficiently</li>
        <li>Track driver performance</li>
        <li>Optimize routes and reduce costs</li>
        <li>Generate comprehensive reports</li>
    </ul>
    <p style="font-size: 16px; line-height: 1.5; margin-bottom: 20px;">
        Check out your dashboard to get started:
    </p>
    """.format(user_name=user_name)
    
    # Create email message using template
    message = get_email_template(
        subject=subject,
        content=content,
        button_text="Go to Dashboard",
        button_url=dashboard_url
    )
    
    # Set recipient
    message["To"] = email
    
    # Send the email
    return await _send_email(
        email=email,
        message=message,
        log_message=f"Welcome email sent to {email}",
        error_message="Failed to send welcome email",
        debug_info=f"\n--- WELCOME EMAIL ---\nTo: {email}\nUser: {user_name}\n--- END EMAIL ---\n"
    )


async def _send_email(email: str, message, log_message: str, error_message: str, debug_info: str = None):
    """
    Helper function to send emails and handle errors
    
    Parameters:
    - email: Recipient email address
    - message: Email message object (MIMEMultipart)
    - log_message: Success log message
    - error_message: Error log message prefix
    - debug_info: Debug information to log
    
    Returns:
    - bool: True if email sent successfully, False otherwise
    """
    # Log debug info if provided
    if debug_info:
        logger.info(debug_info)
    
    # Try to send the email
    try:
        # Check if SMTP credentials are configured
        if not all([settings.SMTP_SERVER, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
            logger.warning("SMTP credentials not configured properly. Email not sent.")
            return False
            
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
            logger.info(log_message)
            return True
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}")
        logger.error(traceback.format_exc())
        return False
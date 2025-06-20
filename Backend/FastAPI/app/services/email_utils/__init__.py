# app/services/__init__.py
"""
Email service module for TRUCKING application.
This module provides functionality for sending different types of emails through the application.

Available Functions:
==================

send_verification_email(email: str, token: str) -> bool
    Purpose: Sends email verification link to new users
    Parameters:
        - email (str): Recipient's email address
        - token (str): Unique verification token for the user
    Returns:
        - bool: True if email sent successfully, False otherwise
    Example:
        success = await send_verification_email("user@example.com", "abc123token")

send_password_reset_email(email: str, token: str) -> bool
    Purpose: Sends password reset link to users who forgot their password
    Parameters:
        - email (str): Recipient's email address  
        - token (str): Unique reset token (valid for 1 hour)
    Returns:
        - bool: True if email sent successfully, False otherwise
    Example:
        success = await send_password_reset_email("user@example.com", "xyz789token")

send_welcome_email(email: str, user_name: str) -> bool
    Purpose: Sends welcome message after successful registration and verification
    Parameters:
        - email (str): Recipient's email address
        - user_name (str): User's display name for personalization
    Returns:
        - bool: True if email sent successfully, False otherwise
    Example:
        success = await send_welcome_email("user@example.com", "John Doe")

Important Notes:
===============
- All functions are async and must be awaited
- Requires proper SMTP configuration in settings (SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD)
- If SMTP not configured, functions return False without sending
- All emails use professional HTML templates with TRUCKING branding
- Errors are automatically logged with detailed information
- Links expire after specified time periods (password reset: 1 hour)

Usage Example:
=============
from app.services import send_verification_email, send_welcome_email

# In an async function
async def register_user(email, username, verification_token):
    # Send verification email
    if await send_verification_email(email, verification_token):
        print("Verification email sent successfully")
    
    # After user verifies, send welcome email
    if await send_welcome_email(email, username):
        print("Welcome email sent successfully")
"""

from .email_utils import (
    send_verification_email,
    send_password_reset_email,
    send_welcome_email
)

# Export functions that should be available when importing from this module
__all__ = [
    'send_verification_email',
    'send_password_reset_email', 
    'send_welcome_email'
]
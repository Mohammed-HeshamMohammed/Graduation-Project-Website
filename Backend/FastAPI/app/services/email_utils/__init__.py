# app/services/__init__.py
"""
Email service module for TRUCKING application.
This module provides functionality for sending different types of emails through the application.
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
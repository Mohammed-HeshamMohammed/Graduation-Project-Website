# app/services/password_handler/exceptions.py
"""
Custom exceptions for password handler module
"""

class PasswordHandlerException(Exception):
    """Base exception for password handler operations"""
    pass

class PasswordValidationError(PasswordHandlerException):
    """Raised when password validation fails"""
    pass

class PasswordHistoryError(PasswordHandlerException):
    """Raised when password history operations fail"""
    pass

class TokenValidationError(PasswordHandlerException):
    """Raised when token validation fails"""
    pass

class UserNotFoundError(PasswordHandlerException):
    """Raised when user is not found"""
    pass

class RateLimitExceededError(PasswordHandlerException):
    """Raised when rate limit is exceeded"""
    pass
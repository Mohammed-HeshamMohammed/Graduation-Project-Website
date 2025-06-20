# File: Password_History/exceptions/password_exceptions.py
"""Custom exceptions for password history management"""

class PasswordHistoryException(Exception):
    """Base exception for password history operations"""
    pass

class PasswordReusedException(PasswordHistoryException):
    """Raised when a password has been used before"""
    pass

class EncryptionException(PasswordHistoryException):
    """Raised when encryption/decryption operations fail"""
    pass

class ValidationException(PasswordHistoryException):
    """Raised when validation fails"""
    pass

class StorageException(PasswordHistoryException):
    """Raised when storage operations fail"""
    pass

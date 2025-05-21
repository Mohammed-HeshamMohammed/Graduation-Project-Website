# app/services/crypto/exceptions.py
from app.middleware.security import SecurityException

class CryptoException(SecurityException):
    """Base exception for all crypto operations"""
    pass

class TamperingDetected(CryptoException):
    """Exception when data tampering is detected"""
    pass

class VersionError(CryptoException):
    """Exception for version-related errors"""
    pass

class DecryptionError(CryptoException):
    """Exception for decryption failures"""
    pass

class EncryptionError(CryptoException):
    """Exception for encryption failures"""
    pass

class KeyManagementError(CryptoException):
    """Exception for key management issues"""
    pass

class FileFormatError(CryptoException):
    """Exception for key storage file format issues"""
    pass
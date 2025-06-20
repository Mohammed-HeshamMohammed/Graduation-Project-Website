# storage_service/exceptions.py
"""Storage service specific exceptions"""

class StorageException(Exception):
    """Base exception for storage operations"""
    pass

class FileOperationException(StorageException):
    """Exception for file operation failures"""
    pass

class LockTimeoutException(StorageException):
    """Exception for file lock timeout"""
    pass

class CorruptedDataException(StorageException):
    """Exception for corrupted data recovery"""
    pass

# app/services/Password_History/services/storage_service/__init__.py
"""
Password History Storage Service

This module provides secure, encrypted storage for user password histories with both
synchronous and asynchronous operations. Data is stored per-user in encrypted files
with obfuscated filenames for additional security.

Architecture Overview:
    FileManager      -> Low-level file operations (encrypt/decrypt, lock/unlock)
    UserStorageService -> High-level user operations (load/save/update histories)
    StorageService   -> Legacy compatibility wrapper
    Exceptions       -> Custom error handling

Typical Usage:
    # Initialize storage service
    storage = UserStorageService()
    
    # Load user's password history
    entries = storage.load_user_history(user_uuid="123", email="user@example.com")
    
    # Add new password entry
    new_entry = {"id": "456", "website": "example.com", "created_at": "2025-01-01"}
    success = storage.add_password_entry(user_uuid="123", email="user@example.com", entry=new_entry)
"""

# 👇 RECOMMENDED: Modern per-user password history storage engine
#    - Encrypts each user's data in separate .enc files
#    - Provides both sync and async operations
#    - Implements caching for performance
#    - Thread-safe with file locking
from .user_storage import UserStorageService

# 👇 LEGACY: Backward compatibility wrapper for old storage format
#    - Maintains compatibility with centralized storage
#    - Provides migration utilities
#    - Deprecated for new development
from .legacy_storage import StorageService

# 👇 ADVANCED: Low-level file access operations
#    - Direct encrypted file read/write operations
#    - File locking mechanisms (sync and async)
#    - Used internally by UserStorageService
#    - Can be used directly for custom storage patterns
from .file_manager import FileManager

# 👇 ERROR HANDLING: Custom exceptions for storage operations
#    - StorageException: Base exception for all storage errors
#    - FileOperationException: File I/O failures
#    - LockTimeoutException: File locking timeouts
#    - CorruptedDataException: Data corruption recovery
from .exceptions import (
    StorageException,
    FileOperationException,
    LockTimeoutException,
    CorruptedDataException
)

# Public API - controls what gets imported with "from storage_service import *"
__all__ = [
    # Primary Classes
    'UserStorageService',   # Main storage service for new applications
    'StorageService',       # Legacy compatibility (migration only)
    'FileManager',          # Direct file operations (advanced usage)
    
    # Exception Handling
    'StorageException',         # Base storage exception
    'FileOperationException',   # File operation failures
    'LockTimeoutException',     # Lock timeout errors
    'CorruptedDataException',   # Data corruption handling
]

# ============================================================================
# QUICK REFERENCE GUIDE
# ============================================================================

"""
UserStorageService - Main API for Password History Storage
=========================================================

INITIALIZATION:
    storage = UserStorageService(data_dir="/optional/custom/path")

SYNC OPERATIONS:
    # Load user's password history
    entries: List[Dict[str, Any]] = storage.load_user_history(
        user_uuid: str,     # User's unique identifier
        email: str          # User's email address
    ) -> List[Dict[str, Any]]  # Returns list of password entries

    # Save complete password history
    success: bool = storage.save_user_history(
        user_uuid: str,                    # User's unique identifier
        email: str,                        # User's email address
        entries: List[Dict[str, Any]]      # Complete list of password entries
    ) -> bool  # Returns True if successful

    # Add single password entry
    success: bool = storage.add_password_entry(
        user_uuid: str,           # User's unique identifier
        email: str,               # User's email address
        entry: Dict[str, Any]     # New password entry to add
    ) -> bool  # Returns True if successful

    # Remove password entry by ID
    success: bool = storage.remove_password_entry(
        user_uuid: str,     # User's unique identifier
        email: str,         # User's email address
        entry_id: str       # ID of entry to remove
    ) -> bool  # Returns True if entry was found and removed

    # Atomic update with custom function
    success: bool = storage.atomic_update_user(
        user_uuid: str,     # User's unique identifier
        email: str,         # User's email address
        update_func: Callable[[List[Dict[str, Any]]], bool]  # Function to modify entries
    ) -> bool  # Returns True if successful

    # Delete all user data
    success: bool = storage.delete_user_history(
        user_uuid: str,     # User's unique identifier
        email: str          # User's email address
    ) -> bool  # Returns True if successful

    # Get user statistics
    stats: Dict[str, Any] = storage.get_user_stats(
        user_uuid: str,     # User's unique identifier
        email: str          # User's email address
    ) -> Dict[str, Any]  # Returns stats like entry_count, file_size, etc.

ASYNC OPERATIONS (same parameters, add 'async_' prefix):
    entries = await storage.async_load_user_history(user_uuid, email)
    success = await storage.async_save_user_history(user_uuid, email, entries)
    success = await storage.async_add_password_entry(user_uuid, email, entry)
    success = await storage.async_remove_password_entry(user_uuid, email, entry_id)
    success = await storage.async_atomic_update_user(user_uuid, email, update_func)
    success = await storage.async_delete_user_history(user_uuid, email)
    stats = await storage.async_get_user_stats(user_uuid, email)

UTILITY OPERATIONS:
    # Create manual backup
    success: bool = storage.create_manual_backup(
        user_uuid: str,                    # User's unique identifier
        email: str,                        # User's email address
        backup_path: str = None            # Optional custom backup path
    ) -> bool

    # System maintenance
    files: List[str] = storage.list_user_files()  # List all user files
    cleanup_stats: Dict = storage.cleanup_stale_locks()  # Clean up old locks
    storage.clear_cache()  # Clear internal cache
    cache_stats: Dict = storage.get_cache_stats()  # Cache performance stats
    system_stats: Dict = storage.get_system_stats()  # Overall system stats

MIGRATION:
    # Migrate from legacy storage
    migration_stats: Dict = storage.migrate_from_old_storage(old_storage_service)

ERROR HANDLING:
    try:
        entries = storage.load_user_history(user_uuid, email)
    except StorageException as e:
        # Handle storage-specific errors
        logger.error(f"Storage error: {e}")
    except FileOperationException as e:
        # Handle file I/O errors
        logger.error(f"File operation failed: {e}")
    except LockTimeoutException as e:
        # Handle lock timeout errors
        logger.error(f"Lock timeout: {e}")

ENTRY FORMAT:
    Password entries should be dictionaries with these common fields:
    {
        "id": str,              # Unique identifier for the entry
        "website": str,         # Website/service name
        "username": str,        # Username/email for the account
        "password_hash": str,   # Hashed password (never store plaintext)
        "created_at": str,      # ISO timestamp of creation
        "updated_at": str,      # ISO timestamp of last update
        "metadata": dict        # Additional metadata
    }

THREAD SAFETY:
    - All operations are thread-safe
    - Uses file locking to prevent concurrent access
    - Async operations use separate locks
    - Cache is thread-safe

SECURITY FEATURES:
    - All data encrypted with AES
    - Filenames obfuscated with hashing
    - Failsafe encryption with multiple algorithms
    - Automatic backup on corruption detection
    - Secure file locking mechanisms
"""

# ============================================================================
# COMPONENT INTERACTION DIAGRAM
# ============================================================================

"""
How Components Work Together:
============================

    Application Code
         |
         v
    UserStorageService  <-- Main API layer
         |                  - Handles caching
         |                  - Manages threading
         |                  - Validates data
         v
    FileManager         <-- File operations layer
         |                  - Encrypts/decrypts data
         |                  - Handles file locking
         |                  - Manages atomic writes
         v
    Encrypted Files     <-- Storage layer
    (*.enc files)           - One file per user
                           - Obfuscated filenames
                           - AES encrypted content

    Exceptions          <-- Error handling
         ^                  - Custom error types
         |                  - Structured error info
    All Layers              - Graceful degradation

Data Flow Example:
1. storage.load_user_history(uuid, email)
2. UserStorageService checks cache
3. If not cached, calls FileManager.read_encrypted_file()
4. FileManager acquires file lock
5. FileManager reads and decrypts file
6. UserStorageService caches result
7. Returns decrypted data to application
"""
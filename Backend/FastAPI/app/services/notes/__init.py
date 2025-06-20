"""
Notes module for managing user notes with company-based access control.

This module provides a complete notes management system with:
- Hierarchical privilege-based access control
- Company-based data isolation
- Encrypted storage with backup functionality
- Comprehensive audit logging
- Search and statistics capabilities

Main Components:
    NotesManager: Primary interface for all notes operations
    Note/NoteCreate/NoteUpdate: Data models for notes
    NotesPrivilegeManager: Access control and privilege validation
    NotesStorage: Encrypted persistence layer
    Custom exceptions: Specific error handling

Example Usage:
    ```python
    from app.services.notes import NotesManager, NoteCreate
    
    # Initialize manager
    notes_manager = NotesManager()
    
    # Create a note
    note_data = NoteCreate(
        content="User showed excellent performance this month",
        target_user_uuid="user-123",
        author_uuid="manager-456"
    )
    
    # Create note with privilege validation
    note = notes_manager.create_note(note_data, ["manager", "admin"])
    
    # Retrieve user notes
    user_notes = notes_manager.get_user_notes(
        user_uuid="user-123",
        requesting_user_uuid="manager-456", 
        requesting_user_privileges=["manager"]
    )
    ```

Required Privileges:
    - Read notes: owner, admin, manager, dispatcher, engineer, fuel_manager, fleet_officer, analyst, viewer
    - Write/Create notes: owner, admin, manager
    - Edit notes: owner, admin, manager (+ original author)
    - Delete notes: owner, admin
    - Export notes: owner, admin
    - View statistics: owner, admin, manager

Data Flow:
    1. API Request → NotesManager
    2. NotesManager → NotesPrivilegeManager (access validation)
    3. NotesManager → UserStorage (user info lookup)
    4. NotesManager → NotesStorage (data persistence)
    5. Response with appropriate models/exceptions
"""

#API Request → NotesManager → [NotesPrivilegeManager + UserStorage + NotesStorage] → Response

from typing import List, Dict, Any, Optional
from .manager import NotesManager
from .models import Note, NoteCreate, NoteUpdate, NoteSearchQuery, NotesStatistics
from .privileges import NotesPrivilegeManager
from .storage import NotesStorage
from .exceptions import (
    NotesException, 
    InsufficientPrivilegesError, 
    NoteNotFoundError,
    InvalidInputError,
    UserNotFoundError,
    CompanyMismatchError,
    StorageError
)

# Version info
__version__ = "1.0.0"
__author__ = "Notes Management System"

# Main exports
__all__ = [
    # Core manager
    'NotesManager',
    
    # Data models
    'Note',
    'NoteCreate', 
    'NoteUpdate',
    'NoteSearchQuery',
    'NotesStatistics',
    
    # Supporting components
    'NotesPrivilegeManager',
    'NotesStorage',
    
    # Exceptions
    'NotesException',
    'InsufficientPrivilegesError',
    'NoteNotFoundError',
    'InvalidInputError',
    'UserNotFoundError',
    'CompanyMismatchError',
    'StorageError',
    
    # Utility functions
    'create_notes_manager',
    'validate_user_privileges'
]

# Convenience functions
def create_notes_manager(user_storage=None, notes_storage=None) -> NotesManager:
    """
    Create a properly configured NotesManager instance.
    
    Args:
        user_storage: Optional UserStorage instance
        notes_storage: Optional NotesStorage instance
        
    Returns:
        NotesManager: Configured notes manager
        
    Example:
        ```python
        manager = create_notes_manager()
        ```
    """
    return NotesManager(user_storage=user_storage, notes_storage=notes_storage)

def validate_user_privileges(privileges: List[str]) -> Dict[str, bool]:
    """
    Get available notes operations for given user privileges.
    
    Args:
        privileges: List of user privilege strings
        
    Returns:
        Dict mapping operation names to boolean permissions
        
    Example:
        ```python
        perms = validate_user_privileges(["manager", "admin"])
        if perms['can_write']:
            # User can create notes
            pass
        ```
    """
    privilege_manager = NotesPrivilegeManager()
    return privilege_manager.get_accessible_privileges(privileges)

# Module configuration
DEFAULT_CONFIG = {
    'max_notes_per_user': 20,
    'cleanup_days': 180,
    'search_limit': 50,
    'backup_retention': 5
}

def get_default_config() -> Dict[str, Any]:
    """Get default configuration for notes module."""
    return DEFAULT_CONFIG.copy()
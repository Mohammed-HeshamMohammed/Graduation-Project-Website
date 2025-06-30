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

__version__ = "1.0.0"
__author__ = "Notes Management System"

__all__ = [
    'NotesManager',
    'Note',
    'NoteCreate', 
    'NoteUpdate',
    'NoteSearchQuery',
    'NotesStatistics',
    'NotesPrivilegeManager',
    'NotesStorage',
    'NotesException',
    'InsufficientPrivilegesError',
    'NoteNotFoundError',
    'InvalidInputError',
    'UserNotFoundError',
    'CompanyMismatchError',
    'StorageError',
    'create_notes_manager',
    'validate_user_privileges'
]

def create_notes_manager(user_storage=None, notes_storage=None):
    return NotesManager(user_storage=user_storage, notes_storage=notes_storage)

def validate_user_privileges(privileges):
    privilege_manager = NotesPrivilegeManager()
    return privilege_manager.get_accessible_privileges(privileges)

DEFAULT_CONFIG = {
    'max_notes_per_user': 20,
    'cleanup_days': 180,
    'search_limit': 50,
    'backup_retention': 5
}

def get_default_config():
    return DEFAULT_CONFIG.copy()
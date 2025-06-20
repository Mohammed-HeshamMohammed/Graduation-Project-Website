"""
Custom exceptions for the notes module.
"""


class NotesException(Exception):
    """Base exception class for notes-related errors."""
    pass


class InsufficientPrivilegesError(NotesException):
    """Raised when user lacks required privileges for an operation."""
    def __init__(self, message="Insufficient privileges to perform this operation"):
        self.message = message
        super().__init__(self.message)


class NoteNotFoundError(NotesException):
    """Raised when a requested note is not found."""
    def __init__(self, note_id=None):
        if note_id:
            self.message = f"Note with ID '{note_id}' not found"
        else:
            self.message = "Note not found"
        super().__init__(self.message)


class InvalidInputError(NotesException):
    """Raised when invalid input is provided."""
    def __init__(self, message="Invalid input provided"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(NotesException):
    """Raised when a user is not found."""
    def __init__(self, user_uuid=None):
        if user_uuid:
            self.message = f"User with UUID '{user_uuid}' not found"
        else:
            self.message = "User not found"
        super().__init__(self.message)


class CompanyMismatchError(NotesException):
    """Raised when users are from different companies."""
    def __init__(self, message="Users must be from the same company"):
        self.message = message
        super().__init__(self.message)


class StorageError(NotesException):
    """Raised when there's an error with data storage operations."""
    def __init__(self, message="Error occurred during storage operation"):
        self.message = message
        super().__init__(self.message)
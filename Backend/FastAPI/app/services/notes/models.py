"""
Data models for the notes module.
"""

import time
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Note:
    """Represents a user note."""
    id: str
    content: str
    author_uuid: str
    author_email: str
    author_name: str
    target_user_uuid: str
    target_user_email: str
    target_user_name: str
    company_uuid: str
    timestamp: float
    created_at: str
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        """Create note from dictionary."""
        return cls(**data)
    
    def is_editable_by(self, user_uuid: str, user_privileges: list) -> bool:
        """Check if note can be edited by given user."""
        # Original author can edit (if they have note creation privileges)
        if self.author_uuid == user_uuid:
            return any(priv in ['owner', 'admin', 'manager'] for priv in user_privileges)
        
        # Only owners can edit others' notes
        return 'owner' in user_privileges
    
    def is_deletable_by(self, user_privileges: list) -> bool:
        """Check if note can be deleted by given user."""
        return any(priv in ['owner', 'admin'] for priv in user_privileges)


@dataclass
class NoteCreate:
    """Data for creating a new note."""
    content: str
    target_user_uuid: str
    author_uuid: str
    
    def validate(self) -> bool:
        """Validate note creation data."""
        return (
            self.content and isinstance(self.content, str) and self.content.strip() and
            self.target_user_uuid and isinstance(self.target_user_uuid, str) and
            self.author_uuid and isinstance(self.author_uuid, str)
        )
    
    def create_note(self, author_info: Dict, target_info: Dict, company_uuid: str) -> Note:
        """Create a Note instance from this creation data."""
        timestamp = time.time()
        note_id = f"note_{int(timestamp)}_{hash(self.content + self.author_uuid) % 10000}"
        
        return Note(
            id=note_id,
            content=self.content.strip(),
            author_uuid=self.author_uuid,
            author_email=author_info.get('email', ''),
            author_name=author_info.get('full_name', ''),
            target_user_uuid=self.target_user_uuid,
            target_user_email=target_info.get('email', ''),
            target_user_name=target_info.get('full_name', ''),
            company_uuid=company_uuid,
            timestamp=timestamp,
            created_at=datetime.now().isoformat()
        )


@dataclass
class NoteUpdate:
    """Data for updating an existing note."""
    note_id: str
    content: str
    updated_by: str
    
    def validate(self) -> bool:
        """Validate note update data."""
        return (
            self.note_id and isinstance(self.note_id, str) and
            self.content and isinstance(self.content, str) and self.content.strip() and
            self.updated_by and isinstance(self.updated_by, str)
        )


@dataclass
class NoteSearchQuery:
    """Search query parameters for notes."""
    search_term: str
    company_uuid: str
    limit: int = 50
    author_uuid: Optional[str] = None
    target_user_uuid: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate search query."""
        return (
            self.search_term and isinstance(self.search_term, str) and
            self.company_uuid and isinstance(self.company_uuid, str) and
            isinstance(self.limit, int) and self.limit > 0
        )


@dataclass
class NotesStatistics:
    """Statistics about notes in the system."""
    total_notes: int = 0
    users_with_notes: int = 0
    notes_by_author: Dict[str, int] = None
    notes_this_month: int = 0
    notes_this_week: int = 0
    notes_today: int = 0
    company_uuid: Optional[str] = None
    
    def __post_init__(self):
        if self.notes_by_author is None:
            self.notes_by_author = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return asdict(self)
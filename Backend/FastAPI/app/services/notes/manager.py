"""
Main manager class for notes operations with company-based access control.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.services.storage import UserStorage
from .models import Note, NoteCreate, NoteUpdate, NoteSearchQuery, NotesStatistics
from .storage import NotesStorage
from .privileges import NotesPrivilegeManager
from .exceptions import (
    NotesException, InsufficientPrivilegesError, NoteNotFoundError,
    InvalidInputError, UserNotFoundError, CompanyMismatchError, StorageError
)

logger = logging.getLogger(__name__)


class NotesManager:
    """Main manager for notes operations with privilege-based access control."""
    
    def __init__(self, user_storage: UserStorage = None, notes_storage: NotesStorage = None):
        """Initialize notes manager with optional storage instances."""
        self.user_storage = user_storage or UserStorage()
        self.notes_storage = notes_storage or NotesStorage()
        self.privilege_manager = NotesPrivilegeManager()
        
        # Load notes data
        self.notes_data = self._load_notes()
        
        logger.info("NotesManager initialized successfully")
    
    def _load_notes(self) -> Dict[str, List[Dict]]:
        """Load notes from storage."""
        try:
            return self.notes_storage.load_notes()
        except StorageError as e:
            logger.error(f"Failed to load notes: {e}")
            return {}
    
    def _save_notes(self) -> bool:
        """Save notes to storage."""
        try:
            # Compact storage before saving
            self.notes_data = self.notes_storage.compact_storage(self.notes_data)
            return self.notes_storage.save_notes(self.notes_data)
        except StorageError as e:
            logger.error(f"Failed to save notes: {e}")
            return False
    
    def _get_user_info(self, user_uuid: str) -> Dict[str, Any]:
        """Get user information by UUID."""
        user = self.user_storage.get_user_by_uuid(user_uuid)
        if not user:
            raise UserNotFoundError(user_uuid)
        return user
    
    def _validate_same_company(self, user1: Dict[str, Any], user2: Dict[str, Any], 
                              requester_privileges: List[str]) -> None:
        """Validate that users are from the same company (unless requester is owner)."""
        if 'owner' in requester_privileges:
            return  # Owners can access across companies
        
        if user1.get('company_id') != user2.get('company_id'):
            raise CompanyMismatchError("Users must be from the same company")
    
    def create_note(self, note_create: NoteCreate, author_privileges: List[str]) -> Note:
        """Create a new note for a user."""
        try:
            # Validate input
            if not note_create.validate():
                raise InvalidInputError("Invalid note creation data")
            
            # Get user information
            author_info = self._get_user_info(note_create.author_uuid)
            target_info = self._get_user_info(note_create.target_user_uuid)
            
            # Validate access permissions
            self.privilege_manager.validate_write_access(author_info, target_info, author_privileges)
            
            # Get company UUID (use target user's company)
            company_uuid = target_info.get('company_id', '')
            
            # Create note instance
            note = note_create.create_note(author_info, target_info, company_uuid)
            
            # Initialize notes for user if not exists
            if note.target_user_uuid not in self.notes_data:
                self.notes_data[note.target_user_uuid] = []
            
            # Add note to storage
            self.notes_data[note.target_user_uuid].append(note.to_dict())
            
            # Save to persistent storage
            if not self._save_notes():
                raise StorageError("Failed to save note")
            
            self.privilege_manager.log_access_attempt(
                "CREATE", note_create.author_uuid, author_privileges, True
            )
            
            logger.info(f"Created note {note.id} for user {note.target_user_uuid} by {note.author_uuid}")
            return note
            
        except (NotesException, StorageError):
            self.privilege_manager.log_access_attempt(
                "CREATE", note_create.author_uuid, author_privileges, False, str(e)
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating note: {e}")
            raise NotesException(f"Failed to create note: {e}")
    
    def get_user_notes(self, user_uuid: str, requesting_user_uuid: str, 
                      requesting_user_privileges: List[str]) -> List[Note]:
        """Get all notes for a specific user."""
        try:
            # Get user information
            target_user = self._get_user_info(user_uuid)
            requesting_user = self._get_user_info(requesting_user_uuid)
            
            # Validate access permissions
            self.privilege_manager.validate_read_access(
                requesting_user, target_user, requesting_user_privileges
            )
            
            # Get notes from storage
            user_notes_data = self.notes_data.get(user_uuid, [])
            
            # Convert to Note objects and sort by timestamp (newest first)
            notes = [Note.from_dict(note_data) for note_data in user_notes_data]
            notes.sort(key=lambda x: x.timestamp, reverse=True)
            
            self.privilege_manager.log_access_attempt(
                "READ", requesting_user_uuid, requesting_user_privileges, True
            )
            
            logger.info(f"Retrieved {len(notes)} notes for user {user_uuid}")
            return notes
            
        except (NotesException, StorageError):
            self.privilege_manager.log_access_attempt(
                "READ", requesting_user_uuid, requesting_user_privileges, False
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user notes: {e}")
            raise NotesException(f"Failed to get user notes: {e}")
    
    def update_note(self, note_update: NoteUpdate, editor_privileges: List[str]) -> Note:
        """Update an existing note."""
        try:
            # Validate input
            if not note_update.validate():
                raise InvalidInputError("Invalid note update data")
            
            # Find the note
            note_found = False
            target_user_uuid = None
            original_note = None
            
            for user_uuid, user_notes in self.notes_data.items():
                for note_data in user_notes:
                    if note_data.get('id') == note_update.note_id:
                        original_note = Note.from_dict(note_data)
                        target_user_uuid = user_uuid
                        note_found = True
                        break
                if note_found:
                    break
            
            if not note_found:
                raise NoteNotFoundError(note_update.note_id)
            
            # Get editor information
            editor_info = self._get_user_info(note_update.updated_by)
            
            # Validate edit permissions
            self.privilege_manager.validate_edit_access(
                editor_info, original_note.author_uuid, editor_privileges
            )
            
            # Update the note
            for note_data in self.notes_data[target_user_uuid]:
                if note_data.get('id') == note_update.note_id:
                    note_data['content'] = note_update.content.strip()
                    note_data['updated_at'] = datetime.now().isoformat()
                    note_data['updated_by'] = note_update.updated_by
                    break
            
            # Save changes
            if not self._save_notes():
                raise StorageError("Failed to save updated note")
            
            # Return updated note
            updated_note = Note.from_dict(note_data)
            
            self.privilege_manager.log_access_attempt(
                "UPDATE", note_update.updated_by, editor_privileges, True
            )
            
            logger.info(f"Updated note {note_update.note_id}")
            return updated_note
            
        except (NotesException, StorageError):
            self.privilege_manager.log_access_attempt(
                "UPDATE", note_update.updated_by, editor_privileges, False
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating note: {e}")
            raise NotesException(f"Failed to update note: {e}")
    
    def delete_note(self, note_id: str, deleter_uuid: str, deleter_privileges: List[str]) -> bool:
        """Delete a note."""
        try:
            # Validate delete permissions
            self.privilege_manager.validate_delete_access(deleter_privileges)
            
            # Find and delete the note
            note_deleted = False
            target_user_uuid = None
            
            for user_uuid, user_notes in self.notes_data.items():
                original_count = len(user_notes)
                self.notes_data[user_uuid] = [
                    note for note in user_notes 
                    if note.get('id') != note_id
                ]
                
                if len(self.notes_data[user_uuid]) < original_count:
                    note_deleted = True
                    target_user_uuid = user_uuid
                    break
            
            if not note_deleted:
                raise NoteNotFoundError(note_id)
            
            # Remove empty note lists
            if not self.notes_data[target_user_uuid]:
                del self.notes_data[target_user_uuid]
            
            # Save changes
            if not self._save_notes():
                raise StorageError("Failed to save after note deletion")
            
            self.privilege_manager.log_access_attempt(
                "DELETE", deleter_uuid, deleter_privileges, True
            )
            
            logger.info(f"Deleted note {note_id}")
            return True
            
        except (NotesException, StorageError):
            self.privilege_manager.log_access_attempt(
                "DELETE", deleter_uuid, deleter_privileges, False
            )
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting note: {e}")
            raise NotesException(f"Failed to delete note: {e}")
    
    def search_notes(self, search_query: NoteSearchQuery, 
                    searcher_privileges: List[str]) -> List[Note]:
        """Search notes within a company."""
        try:
            # Validate search permissions
            self.privilege_manager.validate_search_access(searcher_privileges)
            
            # Validate search query
            if not search_query.validate():
                raise InvalidInputError("Invalid search query")
            
            search_term = search_query.search_term.lower().strip()
            matching_notes = []
            
            for user_uuid, user_notes in self.notes_data.items():
                # Get user to check company
                try:
                    user = self.user_storage.get_user_by_uuid(user_uuid)
                    if not user or user.get('company_id') != search_query.company_uuid:
                        continue
                except:
                    continue  # Skip if user not found
                
                for note_data in user_notes:
                    note = Note.from_dict(note_data)
                    
                    # Apply filters
                    if search_query.author_uuid and note.author_uuid != search_query.author_uuid:
                        continue
                    
                    if search_query.target_user_uuid and note.target_user_uuid != search_query.target_user_uuid:
                        continue
                    
                    # Date filters (if provided)
                    if search_query.start_date:
                        try:
                            start_timestamp = datetime.fromisoformat(search_query.start_date).timestamp()
                            if note.timestamp < start_timestamp:
                                continue
                        except:
                            pass
                    
                    if search_query.end_date:
                        try:
                            end_timestamp = datetime.fromisoformat(search_query.end_date).timestamp()
                            if note.timestamp > end_timestamp:
                                continue
                        except:
                            pass
                    
                    # Text search
                    searchable_text = ' '.join([
                        note.content,
                        note.author_name,
                        note.target_user_name,
                        note.target_user_email
                    ]).lower()
                    
                    if search_term in searchable_text:
                        matching_notes.append(note)
                        
                        if len(matching_notes) >= search_query.limit:
                            break
                
                if len(matching_notes) >= search_query.limit:
                    break
            
            # Sort by timestamp (newest first)
            matching_notes.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"Search found {len(matching_notes)} matching notes")
            return matching_notes
            
        except (NotesException, StorageError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching notes: {e}")
            raise NotesException(f"Failed to search notes: {e}")
    
    def get_notes_by_author(self, author_uuid: str, company_uuid: str, 
                           requester_privileges: List[str]) -> List[Note]:
        """Get all notes created by a specific author within a company."""
        try:
            # Validate read permissions
            self.privilege_manager.validate_read_access(
                {'company_id': company_uuid}, {'company_id': company_uuid}, requester_privileges
            )
            
            author_notes = []
            
            for user_uuid, user_notes in self.notes_data.items():
                for note_data in user_notes:
                    note = Note.from_dict(note_data)
                    
                    # Filter by author and company
                    if (note.author_uuid == author_uuid and 
                        note.company_uuid == company_uuid):
                        author_notes.append(note)
            
            # Sort by timestamp (newest first)
            author_notes.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"Found {len(author_notes)} notes by author {author_uuid}")
            return author_notes
            
        except (NotesException, StorageError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting notes by author: {e}")
            raise NotesException(f"Failed to get notes by author: {e}")
    
    def get_statistics(self, company_uuid: str = None, 
                      requester_privileges: List[str] = None) -> NotesStatistics:
        """Get notes statistics, optionally filtered by company."""
        try:
            if requester_privileges:
                self.privilege_manager.validate_statistics_access(requester_privileges)
            
            stats = NotesStatistics(company_uuid=company_uuid)
            
            current_time = time.time()
            month_ago = current_time - (30 * 24 * 60 * 60)
            week_ago = current_time - (7 * 24 * 60 * 60)
            day_ago = current_time - (24 * 60 * 60)
            
            for user_uuid, user_notes in self.notes_data.items():
                # Filter by company if specified
                if company_uuid:
                    try:
                        user = self.user_storage.get_user_by_uuid(user_uuid)
                        if not user or user.get('company_id') != company_uuid:
                            continue
                    except:
                        continue
                
                if user_notes:
                    stats.users_with_notes += 1
                    stats.total_notes += len(user_notes)
                    
                    for note_data in user_notes:
                        note = Note.from_dict(note_data)
                        
                        # Count by author
                        author_name = note.author_name or 'Unknown'
                        stats.notes_by_author[author_name] = stats.notes_by_author.get(author_name, 0) + 1
                        
                        # Count by time period
                        if note.timestamp > month_ago:
                            stats.notes_this_month += 1
                        if note.timestamp > week_ago:
                            stats.notes_this_week += 1
                        if note.timestamp > day_ago:
                            stats.notes_today += 1
            
            return stats
            
        except (NotesException, StorageError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting statistics: {e}")
            raise NotesException(f"Failed to get statistics: {e}")
    
    def export_user_notes(self, user_uuid: str, exporter_privileges: List[str]) -> Optional[Dict[str, Any]]:
        """Export all notes for a user."""
        try:
            # Validate export permissions
            self.privilege_manager.validate_export_access(exporter_privileges)
            
            # Get user info
            user_info = self._get_user_info(user_uuid)
            
            # Get notes
            user_notes_data = self.notes_data.get(user_uuid, [])
            if not user_notes_data:
                return None
            
            # Convert to Note objects and sort
            notes = [Note.from_dict(note_data) for note_data in user_notes_data]
            notes.sort(key=lambda x: x.timestamp)
            
            export_data = {
                'user_info': {
                    'uuid': user_uuid,
                    'email': user_info.get('email', ''),
                    'name': user_info.get('full_name', ''),
                    'company_id': user_info.get('company_id', '')
                },
                'notes': [note.to_dict() for note in notes],
                'export_timestamp': datetime.now().isoformat(),
                'total_notes': len(notes)
            }
            
            logger.info(f"Exported {len(notes)} notes for user {user_uuid}")
            return export_data
            
        except (NotesException, StorageError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error exporting notes: {e}")
            raise NotesException(f"Failed to export notes: {e}")
    
    def get_note_by_id(self, note_id: str, requester_privileges: List[str]) -> Optional[Note]:
        """Get a specific note by ID."""
        try:
            # Validate read permissions
            self.privilege_manager.validate_read_access(
                {}, {}, requester_privileges  # Basic read permission check
            )
            
            for user_uuid, user_notes in self.notes_data.items():
                for note_data in user_notes:
                    if note_data.get('id') == note_id:
                        return Note.from_dict(note_data)
            
            raise NoteNotFoundError(note_id)
            
        except (NotesException, StorageError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting note by ID: {e}")
            raise NotesException(f"Failed to get note by ID: {e}")
    
    def cleanup_old_notes(self, days_old: int = 180, max_notes_per_user: int = 20) -> int:
        """Clean up old notes while keeping a minimum number per user."""
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            for user_uuid in list(self.notes_data.keys()):
                if user_uuid in self.notes_data:
                    user_notes_data = self.notes_data[user_uuid]
                    original_count = len(user_notes_data)
                    
                    # Convert to Note objects and sort by timestamp (newest first)
                    notes = [Note.from_dict(note_data) for note_data in user_notes_data]
                    notes.sort(key=lambda x: x.timestamp, reverse=True)
                    
                    # Keep the most recent max_notes_per_user notes regardless of age
                    if len(notes) > max_notes_per_user:
                        recent_notes = notes[:max_notes_per_user]
                        # From the older notes, keep only those newer than cutoff
                        older_notes = [note for note in notes[max_notes_per_user:] 
                                     if note.timestamp > cutoff_time]
                        kept_notes = recent_notes + older_notes
                    else:
                        # If under limit, just remove very old notes but keep at least 5
                        if len(notes) > 5:
                            kept_notes = notes[:5] + [
                                note for note in notes[5:] 
                                if note.timestamp > cutoff_time
                            ]
                        else:
                            kept_notes = notes
                    
                    # Update storage with kept notes
                    self.notes_data[user_uuid] = [note.to_dict() for note in kept_notes]
                    cleaned_count += original_count - len(kept_notes)
                    
                    # Remove empty entries
                    if not self.notes_data[user_uuid]:
                        del self.notes_data[user_uuid]
            
            # Save cleaned data
            if cleaned_count > 0:
                if self._save_notes():
                    logger.info(f"Cleaned up {cleaned_count} old notes")
                else:
                    logger.error("Failed to save after cleanup")
                    return 0
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old notes: {e}")
            return 0
    
    def get_user_privileges(self, user_privileges: List[str]) -> Dict[str, bool]:
        """Get notes privileges for a user."""
        return self.privilege_manager.get_accessible_privileges(user_privileges)
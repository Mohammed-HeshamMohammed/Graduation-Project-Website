"""
File handler for managing different types of encrypted storage files.
"""

import os
import logging
import threading
from pathlib import Path
from typing import Dict, Any, NamedTuple
from app.config import settings
from .base_storage import BaseStorage

logger = logging.getLogger(__name__)


class OperationResult(NamedTuple):
    """Result of a storage operation."""
    success: bool
    message: str
    data: Any = None


class FileHandler(BaseStorage):
    """Handler for managing different types of storage files with thread safety."""
    
    def __init__(self):
        """Initialize file handler with file paths and thread safety."""
        super().__init__()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Define file paths
        self.user_data_path = self.data_dir / settings.USER_DATA_FILE
        self.notes_path = self.data_dir / "user_notes.enc"
        self.messages_path = self.data_dir / "user_messages.enc"
    
    def load_users(self) -> Dict[str, Any]:
        """Load users from encrypted file with enhanced error handling."""
        with self._lock:
            try:
                users = self.load_encrypted_data(self.user_data_path, "users")
                
                # Special handling for corrupted user data
                if not users and self.user_data_path.exists():
                    try:
                        # If file exists but couldn't be loaded, it might be corrupted
                        with open(self.user_data_path, 'rb') as f:
                            if f.read():  # File has content but couldn't be decrypted
                                self._create_backup_and_reset(self.user_data_path)
                    except Exception as e:
                        logger.error(f"Error checking user data file: {e}")
                
                logger.info(f"Loaded {len(users)} user(s) from storage")
                return users
            except Exception as e:
                logger.error(f"load_users: {type(e).__name__}: {e}")
                return {}
    
    def save_users(self, users: Dict[str, Any]) -> OperationResult:
        """Save users to encrypted file with structured result."""
        with self._lock:
            try:
                if not isinstance(users, dict):
                    return OperationResult(False, "Invalid users data type")
                
                success = self.save_encrypted_data(users, self.user_data_path, "users")
                if success:
                    return OperationResult(True, f"Successfully saved {len(users)} users")
                else:
                    return OperationResult(False, "Failed to save users to file")
            except Exception as e:
                logger.error(f"save_users: {type(e).__name__}: {e}")
                return OperationResult(False, str(e))
    
    def load_notes(self) -> Dict[str, Any]:
        """Load notes from encrypted file."""
        with self._lock:
            try:
                notes = self.load_encrypted_data(self.notes_path, "notes")
                logger.info(f"Loaded notes for {len(notes)} user(s)")
                return notes
            except Exception as e:
                logger.error(f"load_notes: {type(e).__name__}: {e}")
                return {}
    
    def save_notes(self, notes: Dict[str, Any]) -> OperationResult:
        """Save notes to encrypted file with structured result."""
        with self._lock:
            try:
                if not isinstance(notes, dict):
                    return OperationResult(False, "Invalid notes data type")
                
                success = self.save_encrypted_data(notes, self.notes_path, "notes")
                if success:
                    return OperationResult(True, f"Successfully saved notes for {len(notes)} users")
                else:
                    return OperationResult(False, "Failed to save notes to file")
            except Exception as e:
                logger.error(f"save_notes: {type(e).__name__}: {e}")
                return OperationResult(False, str(e))
    
    def load_messages(self) -> Dict[str, Any]:
        """Load messages from encrypted file."""
        with self._lock:
            try:
                messages = self.load_encrypted_data(self.messages_path, "messages")
                logger.info(f"Loaded messages for {len(messages)} user(s)")
                return messages
            except Exception as e:
                logger.error(f"load_messages: {type(e).__name__}: {e}")
                return {}
    
    def save_messages(self, messages: Dict[str, Any]) -> OperationResult:
        """Save messages to encrypted file with structured result."""
        with self._lock:
            try:
                if not isinstance(messages, dict):
                    return OperationResult(False, "Invalid messages data type")
                
                success = self.save_encrypted_data(messages, self.messages_path, "messages")
                if success:
                    return OperationResult(True, f"Successfully saved messages for {len(messages)} users")
                else:
                    return OperationResult(False, "Failed to save messages to file")
            except Exception as e:
                logger.error(f"save_messages: {type(e).__name__}: {e}")
                return OperationResult(False, str(e))
    
    def cleanup_user_files(self, user_uuid: str, users: Dict[str, Any], 
                          notes: Dict[str, Any], messages: Dict[str, Any]) -> OperationResult:
        with self._lock:
            try:
                errors = []
                
                # Remove notes
                if user_uuid in notes:
                    del notes[user_uuid]
                    result = self.save_notes(notes)
                    if not result.success:
                        errors.append(f"Failed to save notes: {result.message}")
                
                # Remove messages
                if user_uuid in messages:
                    del messages[user_uuid]
                    result = self.save_messages(messages)
                    if not result.success:
                        errors.append(f"Failed to save messages: {result.message}")
                
                if errors:
                    msg = f"Partial cleanup failure for user {user_uuid}: {'; '.join(errors)}"
                    logger.warning(msg)
                    return OperationResult(False, msg)
                else:
                    msg = f"Successfully cleaned up data for deleted user: {user_uuid}"
                    logger.info(msg)
                    return OperationResult(True, msg)
            except Exception as e:
                msg = f"Error cleaning up user data for {user_uuid}: {type(e).__name__}: {e}"
                logger.error(msg)
                return OperationResult(False, msg)
    
    def validate_data_integrity(self, users: Dict[str, Any], notes: Dict[str, Any], 
                               messages: Dict[str, Any]) -> OperationResult:
        try:
            issues = []
            
            # Get all user UUIDs
            user_uuids = set()
            for user_data in users.values():
                if isinstance(user_data, dict) and 'uuid' in user_data:
                    user_uuids.add(user_data['uuid'])
            
            # Check for orphaned notes
            orphaned_notes = set(notes.keys()) - user_uuids
            if orphaned_notes:
                issues.append(f"Orphaned notes found for UUIDs: {orphaned_notes}")
            
            # Check for orphaned messages
            orphaned_messages = set(messages.keys()) - user_uuids
            if orphaned_messages:
                issues.append(f"Orphaned messages found for UUIDs: {orphaned_messages}")
            
            # Check for duplicate UUIDs in users
            uuid_counts = {}
            for email, user_data in users.items():
                if isinstance(user_data, dict) and 'uuid' in user_data:
                    uuid = user_data['uuid']
                    uuid_counts[uuid] = uuid_counts.get(uuid, 0) + 1
            
            duplicate_uuids = {uuid: count for uuid, count in uuid_counts.items() if count > 1}
            if duplicate_uuids:
                issues.append(f"Duplicate UUIDs found: {duplicate_uuids}")
            
            # Check for users without required fields
            invalid_users = []
            for email, user_data in users.items():
                if not isinstance(user_data, dict):
                    invalid_users.append(f"{email}: not a dictionary")
                elif 'uuid' not in user_data:
                    invalid_users.append(f"{email}: missing UUID")
                elif 'company_id' not in user_data:
                    invalid_users.append(f"{email}: missing company_id")
            
            if invalid_users:
                issues.append(f"Invalid user records: {invalid_users}")
            
            if issues:
                issue_summary = "; ".join(issues)
                logger.warning(f"Data integrity issues found: {issue_summary}")
                return OperationResult(False, f"Data integrity issues: {issue_summary}", 
                                     {'issues': issues})
            else:
                msg = "Data integrity validation passed"
                logger.info(msg)
                return OperationResult(True, msg, {
                    'user_count': len(users),
                    'notes_count': len(notes),
                    'messages_count': len(messages),
                    'unique_uuids': len(user_uuids)
                })
        except Exception as e:
            msg = f"Error during data integrity validation: {type(e).__name__}: {e}"
            logger.error(msg)
            return OperationResult(False, msg)
    
    def get_file_stats(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            stats = {}
            
            files = {
                'users': self.user_data_path,
                'notes': self.notes_path,
                'messages': self.messages_path
            }
            
            for file_type, file_path in files.items():
                try:
                    if file_path.exists():
                        stat = file_path.stat()
                        stats[file_type] = {
                            'exists': True,
                            'size_bytes': stat.st_size,
                            'modified_time': stat.st_mtime,
                            'readable': os.access(file_path, os.R_OK),
                            'writable': os.access(file_path, os.W_OK)
                        }
                    else:
                        stats[file_type] = {
                            'exists': False,
                            'size_bytes': 0,
                            'modified_time': None,
                            'readable': False,
                            'writable': False
                        }
                except Exception as e:
                    logger.error(f"Error getting stats for {file_type}: {e}")
                    stats[file_type] = {
                        'exists': False,
                        'error': str(e)
                    }
            
            return stats
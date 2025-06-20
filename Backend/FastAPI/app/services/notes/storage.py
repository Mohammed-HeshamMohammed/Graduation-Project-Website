"""
Storage layer for notes data persistence.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.services.crypto import encrypt_data, decrypt_data, encrypt_with_failsafe, decrypt_with_failsafe, CryptoException
from app.config import settings
from .models import Note, NotesStatistics
from .exceptions import StorageError

logger = logging.getLogger(__name__)


class NotesStorage:
    """Handles persistent storage of notes data."""
    
    def __init__(self, data_dir: str = None):
        """Initialize storage with optional custom data directory."""
        self.data_dir = Path(data_dir) if data_dir else Path(settings.DATA_DIR)
        self.notes_path = self.data_dir / "user_notes.enc"
        self.backup_path = self.data_dir / "user_notes.bak"
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"NotesStorage initialized with path: {self.notes_path}")
    
    def load_notes(self) -> Dict[str, List[Dict]]:
        """Load notes from encrypted storage."""
        if not os.path.exists(self.notes_path):
            logger.info("Notes file does not exist, returning empty notes store")
            return {}
        
        try:
            with open(self.notes_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.warning("Notes file is empty")
                    return {}
                
                # Try to decrypt with failsafe first, then fallback
                try:
                    decrypted_data = decrypt_with_failsafe(encrypted_data, client_ip='127.0.0.1')
                except CryptoException:
                    try:
                        decrypted_data = decrypt_data(encrypted_data, client_ip='127.0.0.1')
                    except CryptoException as e:
                        logger.error(f"Failed to decrypt notes: {e}")
                        raise StorageError(f"Unable to decrypt notes data: {e}")
                
                notes_data = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Loaded notes for {len(notes_data)} user(s)")
                return notes_data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in notes file: {e}")
            raise StorageError(f"Corrupted notes data: {e}")
        except Exception as e:
            logger.error(f"Error loading notes: {type(e).__name__}: {e}")
            raise StorageError(f"Failed to load notes: {e}")
    
    def save_notes(self, notes_data: Dict[str, List[Dict]]) -> bool:
        """Save notes to encrypted storage with backup."""
        try:
            # Create backup of existing file
            self._create_backup()
            
            # Prepare data for encryption
            data_json = json.dumps(notes_data, indent=2, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # Encrypt data with failsafe, fallback to regular encryption
            try:
                encrypted_data = encrypt_with_failsafe(data_bytes, client_ip='127.0.0.1')
            except CryptoException as e:
                logger.warning(f"Failsafe encryption failed, using regular encryption: {e}")
                try:
                    encrypted_data = encrypt_data(data_bytes, client_ip='127.0.0.1')
                except CryptoException as fallback_error:
                    logger.error(f"All encryption methods failed: {fallback_error}")
                    raise StorageError(f"Encryption failed: {fallback_error}")
            
            # Write to temporary file first, then atomic move
            temp_path = self.notes_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Atomic move to final location
                temp_path.replace(self.notes_path)
                
                logger.info(f"Successfully saved notes data ({len(data_bytes)} bytes)")
                return True
                
            except Exception as write_error:
                logger.error(f"Error writing encrypted notes: {write_error}")
                # Clean up temp file
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                raise StorageError(f"Failed to write notes: {write_error}")
                
        except Exception as e:
            logger.error(f"Error saving notes: {type(e).__name__}: {e}")
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of current notes file."""
        if not self.notes_path.exists():
            return True
        
        try:
            backup_data = self.notes_path.read_bytes()
            self.backup_path.write_bytes(backup_data)
            logger.debug(f"Created backup at {self.backup_path}")
            return True
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
            return False
    
    def restore_from_backup(self) -> bool:
        """Restore notes from backup file."""
        if not self.backup_path.exists():
            logger.warning("No backup file exists")
            return False
        
        try:
            backup_data = self.backup_path.read_bytes()
            self.notes_path.write_bytes(backup_data)
            logger.info("Restored notes from backup")
            return True
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            backup_pattern = self.data_dir.glob("user_notes.bak*")
            backup_files = sorted(backup_pattern, key=lambda p: p.stat().st_mtime, reverse=True)
            
            cleaned_count = 0
            for backup_file in backup_files[keep_count:]:
                try:
                    backup_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete backup {backup_file}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old backup files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
            return 0
    
    def get_storage_info(self) -> Dict[str, any]:
        """Get information about storage files."""
        info = {
            'notes_file_exists': self.notes_path.exists(),
            'backup_file_exists': self.backup_path.exists(),
            'notes_file_size': 0,
            'backup_file_size': 0,
            'notes_modified': None,
            'backup_modified': None
        }
        
        try:
            if self.notes_path.exists():
                stat = self.notes_path.stat()
                info['notes_file_size'] = stat.st_size
                info['notes_modified'] = stat.st_mtime
            
            if self.backup_path.exists():
                stat = self.backup_path.stat()
                info['backup_file_size'] = stat.st_size
                info['backup_modified'] = stat.st_mtime
                
        except Exception as e:
            logger.error(f"Error getting storage info: {e}")
        
        return info
    
    def verify_data_integrity(self, notes_data: Dict[str, List[Dict]]) -> bool:
        """Verify the integrity of notes data structure."""
        try:
            if not isinstance(notes_data, dict):
                logger.error("Notes data is not a dictionary")
                return False
            
            for user_uuid, user_notes in notes_data.items():
                if not isinstance(user_uuid, str):
                    logger.error(f"Invalid user UUID type: {type(user_uuid)}")
                    return False
                
                if not isinstance(user_notes, list):
                    logger.error(f"User notes is not a list for user {user_uuid}")
                    return False
                
                for note_data in user_notes:
                    if not isinstance(note_data, dict):
                        logger.error(f"Note is not a dictionary for user {user_uuid}")
                        return False
                    
                    # Check required fields
                    required_fields = ['id', 'content', 'author_uuid', 'timestamp', 'company_uuid']
                    for field in required_fields:
                        if field not in note_data:
                            logger.error(f"Missing required field '{field}' in note for user {user_uuid}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying data integrity: {e}")
            return False
    
    def compact_storage(self, notes_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Remove empty entries and optimize storage."""
        try:
            compacted = {}
            
            for user_uuid, user_notes in notes_data.items():
                # Only keep users who have notes
                if user_notes:
                    # Sort notes by timestamp (newest first) and remove duplicates
                    seen_ids = set()
                    unique_notes = []
                    
                    for note in sorted(user_notes, key=lambda x: x.get('timestamp', 0), reverse=True):
                        note_id = note.get('id')
                        if note_id and note_id not in seen_ids:
                            seen_ids.add(note_id)
                            unique_notes.append(note)
                    
                    if unique_notes:
                        compacted[user_uuid] = unique_notes
            
            removed_users = len(notes_data) - len(compacted)
            if removed_users > 0:
                logger.info(f"Compacted storage: removed {removed_users} empty user entries")
            
            return compacted
            
        except Exception as e:
            logger.error(f"Error compacting storage: {e}")
            return notes_data
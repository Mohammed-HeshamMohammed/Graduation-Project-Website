import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any
from app.services.storage import UserStorage
from app.services.notes import NotesManager
from app.services.Password_History.models import PasswordHistoryManager
from app.services.messaging import MessagingService

# Configure logging
logger = logging.getLogger(__name__)


class DataManager:
    """Handles data backup, statistics, and cleanup operations"""
    
    def __init__(self, storage: UserStorage, notes_manager: NotesManager, 
                 password_history_manager: PasswordHistoryManager, 
                 messaging_service: MessagingService):
        """
        Initialize data manager
        
        Args:
            storage: UserStorage instance
            notes_manager: NotesManager instance
            password_history_manager: PasswordHistoryManager instance
            messaging_service: MessagingService instance
        """
        self.storage = storage
        self.notes_manager = notes_manager
        self.password_history_manager = password_history_manager
        self.messaging_service = messaging_service
    
    def backup_data(self, backup_path: str = None) -> bool:
        """
        Create a manual backup of all data
        
        Args:
            backup_path: Optional specific path for backup, if None creates timestamped backup
            
        Returns:
            bool: True if backup was successful
        """
        try:
            if backup_path is None:
                timestamp = int(time.time())
                backup_dir = self.storage.data_dir / f"backup_{timestamp}"
                os.makedirs(backup_dir, exist_ok=True)
            else:
                backup_dir = Path(backup_path)
                os.makedirs(backup_dir, exist_ok=True)
            
            # Backup all data files
            backups = {
                'users': self.storage.users,
                'password_history': self.password_history_manager.password_history,
                'notes': self.notes_manager.notes,
                'messages': self.messaging_service.messages
            }
            
            for name, data in backups.items():
                backup_file = backup_dir / f"{name}_backup.json"
                with open(backup_file, 'w') as f:
                    json.dump(data, f, indent=2, sort_keys=True)
            
            logger.info(f"Backup created at {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {type(e).__name__}: {e}")
            return False
    
    def get_user_statistics(self, company_id: str = None) -> Dict[str, Any]:
        """
        Get user statistics, optionally filtered by company
        
        Args:
            company_id: Optional company ID to filter statistics
            
        Returns:
            Dict containing various user statistics
        """
        try:
            stats = {
                'total_users': 0,
                'verified_users': 0,
                'logged_in_users': 0,
                'owners': 0,
                'privilege_breakdown': {},
                'company_breakdown': {},
                'notes_stats': {},
                'password_history_stats': {},
                'message_stats': {}
            }
            
            # Calculate user statistics
            stats.update(self._calculate_user_stats(company_id))
            
            # Add notes statistics
            try:
                stats['notes_stats'] = self.notes_manager.get_notes_statistics(company_id)
            except Exception as e:
                logger.error(f"Error getting notes statistics: {e}")
                stats['notes_stats'] = {}
            
            # Add password history statistics
            try:
                stats['password_history_stats'] = self.password_history_manager.get_password_history_stats()
            except Exception as e:
                logger.error(f"Error getting password history statistics: {e}")
                stats['password_history_stats'] = {}
            
            # Add message statistics
            try:
                stats['message_stats'] = self.messaging_service.get_message_statistics(company_id=company_id)
            except Exception as e:
                logger.error(f"Error getting message statistics: {e}")
                stats['message_stats'] = {}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {type(e).__name__}: {e}")
            return {}
    
    def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        """
        Clean up old messages and notes (for maintenance)
        
        Args:
            days_old: Number of days after which data is considered old
            
        Returns:
            Dict with counts of cleaned items
        """
        try:
            cleaned_messages = 0
            cleaned_notes = 0
            
            # Clean old messages using messaging service
            try:
                cleaned_messages = self.messaging_service.cleanup_old_messages(days_old)
                if cleaned_messages > 0:
                    logger.info(f"Cleaned {cleaned_messages} old messages")
            except Exception as e:
                logger.error(f"Error cleaning messages: {e}")
            
            # Clean old notes using notes manager
            try:
                cleaned_notes = self.notes_manager.cleanup_old_notes(days_old * 2)  # Keep notes longer
                if cleaned_notes > 0:
                    logger.info(f"Cleaned {cleaned_notes} old notes")
            except Exception as e:
                logger.error(f"Error cleaning notes: {e}")
            
            # Clean up orphaned password histories
            try:
                self.password_history_manager.cleanup_orphaned_histories()
            except Exception as e:
                logger.error(f"Error cleaning password histories: {e}")
            
            return {
                'cleaned_messages': cleaned_messages,
                'cleaned_notes': cleaned_notes
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {type(e).__name__}: {e}")
            return {'cleaned_messages': 0, 'cleaned_notes': 0}
    
    def _calculate_user_stats(self, company_id: str = None) -> Dict[str, Any]:
        """
        Calculate user-related statistics
        
        Args:
            company_id: Optional company ID to filter by
            
        Returns:
            Dict with user statistics
        """
        stats = {
            'total_users': 0,
            'verified_users': 0,
            'logged_in_users': 0,
            'owners': 0,
            'privilege_breakdown': {},
            'company_breakdown': {}
        }
        
        for user_data in self.storage.users.values():
            if not isinstance(user_data, dict):
                continue
            
            # Filter by company if specified
            if company_id and user_data.get('company_id') != company_id:
                continue
            
            stats['total_users'] += 1
            
            if user_data.get('verified'):
                stats['verified_users'] += 1
            
            if user_data.get('is_logged_in'):
                stats['logged_in_users'] += 1
            
            if user_data.get('is_owner'):
                stats['owners'] += 1
            
            # Privilege breakdown
            privileges = user_data.get('privileges', [])
            for priv in privileges:
                stats['privilege_breakdown'][priv] = stats['privilege_breakdown'].get(priv, 0) + 1
            
            # Company breakdown (only if not filtering by company)
            if not company_id:
                user_company = user_data.get('company_id', 'unknown')
                stats['company_breakdown'][user_company] = stats['company_breakdown'].get(user_company, 0) + 1
        
        return stats
    
    def export_data(self, export_path: str, data_types: list = None) -> bool:
        """
        Export specific data types to a file
        
        Args:
            export_path: Path where to export the data
            data_types: List of data types to export (users, notes, messages, password_history)
            
        Returns:
            bool: True if export was successful
        """
        try:
            if data_types is None:
                data_types = ['users', 'notes', 'messages', 'password_history']
            
            export_data = {}
            
            if 'users' in data_types:
                # Export sanitized user data (remove sensitive information)
                export_data['users'] = self._sanitize_user_data_for_export()
            
            if 'notes' in data_types:
                export_data['notes'] = self.notes_manager.notes
            
            if 'messages' in data_types:
                export_data['messages'] = self.messaging_service.messages
            
            if 'password_history' in data_types:
                # Don't export actual password hashes for security
                export_data['password_history'] = self._sanitize_password_history_for_export()
            
            # Write to file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
            
            logger.info(f"Data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting data: {type(e).__name__}: {e}")
            return False
    
    def get_data_size_info(self) -> Dict[str, Any]:
        """
        Get information about data sizes
        
        Returns:
            Dict with size information for different data types
        """
        try:
            size_info = {
                'users_count': len(self.storage.users),
                'notes_count': len(getattr(self.notes_manager, 'notes', {})),
                'messages_count': len(getattr(self.messaging_service, 'messages', {})),
                'password_history_count': len(getattr(self.password_history_manager, 'password_history', {}))
            }
            
            # Calculate estimated memory usage (rough estimate)
            size_info['estimated_memory_kb'] = (
                len(str(self.storage.users)) + 
                len(str(getattr(self.notes_manager, 'notes', {}))) +
                len(str(getattr(self.messaging_service, 'messages', {}))) +
                len(str(getattr(self.password_history_manager, 'password_history', {})))
            ) / 1024
            
            return size_info
            
        except Exception as e:
            logger.error(f"Error getting data size info: {type(e).__name__}: {e}")
            return {}
    
    def _sanitize_user_data_for_export(self) -> Dict[str, Any]:
        """Sanitize user data for export by removing sensitive information"""
        sanitized = {}
        
        for email, user_data in self.storage.users.items():
            if isinstance(user_data, dict):
                sanitized_user = user_data.copy()
                # Remove sensitive fields
                sanitized_user.pop('password', None)
                sanitized_user.pop('reset_token', None)
                sanitized_user.pop('verification_token', None)
                sanitized[email] = sanitized_user
        
        return sanitized
    
    def _sanitize_password_history_for_export(self) -> Dict[str, Any]:
        """Sanitize password history for export"""
        sanitized = {}
        
        password_history = getattr(self.password_history_manager, 'password_history', {})
        for user_uuid, history in password_history.items():
            if isinstance(history, list):
                # Only export metadata, not actual password hashes
                sanitized[user_uuid] = [
                    {
                        'timestamp': entry.get('timestamp'),
                        'hash_length': len(entry.get('password_hash', ''))
                    }
                    for entry in history
                    if isinstance(entry, dict)
                ]
        
        return sanitized
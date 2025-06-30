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

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, storage: UserStorage, notes_manager: NotesManager, 
                 password_history_manager: PasswordHistoryManager, 
                 messaging_service: MessagingService):
        self.storage = storage
        self.notes_manager = notes_manager
        self.password_history_manager = password_history_manager
        self.messaging_service = messaging_service

    def backup_data(self, backup_path: str = None) -> bool:
        try:
            backup_dir = Path(backup_path) if backup_path else self.storage.data_dir / f"backup_{int(time.time())}"
            os.makedirs(backup_dir, exist_ok=True)
            backups = {
                'users': self.storage.users,
                'password_history': self.password_history_manager.password_history,
                'notes': self.notes_manager.notes,
                'messages': self.messaging_service.messages
            }
            for name, data in backups.items():
                with open(backup_dir / f"{name}_backup.json", 'w') as f:
                    json.dump(data, f, indent=2, sort_keys=True)
            logger.info(f"Backup created at {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {type(e).__name__}: {e}")
            return False

    def get_user_statistics(self, company_id: str = None) -> Dict[str, Any]:
        try:
            stats = self._calculate_user_stats(company_id)
            stats['notes_stats'] = self._safe_call(self.notes_manager.get_notes_statistics, company_id)
            stats['password_history_stats'] = self._safe_call(self.password_history_manager.get_password_history_stats)
            stats['message_stats'] = self._safe_call(self.messaging_service.get_message_statistics, company_id=company_id)
            return stats
        except Exception as e:
            logger.error(f"Error getting user statistics: {type(e).__name__}: {e}")
            return {}

    def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        try:
            cleaned_messages = self._safe_call(self.messaging_service.cleanup_old_messages, days_old) or 0
            cleaned_notes = self._safe_call(self.notes_manager.cleanup_old_notes, days_old * 2) or 0
            self._safe_call(self.password_history_manager.cleanup_orphaned_histories)
            return {'cleaned_messages': cleaned_messages, 'cleaned_notes': cleaned_notes}
        except Exception as e:
            logger.error(f"Error cleaning up old data: {type(e).__name__}: {e}")
            return {'cleaned_messages': 0, 'cleaned_notes': 0}

    def export_data(self, export_path: str, data_types: list = None) -> bool:
        try:
            data_types = data_types or ['users', 'notes', 'messages', 'password_history']
            export_data = {}
            if 'users' in data_types:
                export_data['users'] = self._sanitize_user_data_for_export()
            if 'notes' in data_types:
                export_data['notes'] = self.notes_manager.notes
            if 'messages' in data_types:
                export_data['messages'] = self.messaging_service.messages
            if 'password_history' in data_types:
                export_data['password_history'] = self._sanitize_password_history_for_export()
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
            logger.info(f"Data exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting data: {type(e).__name__}: {e}")
            return False

    def get_data_size_info(self) -> Dict[str, Any]:
        try:
            size_info = {
                'users_count': len(self.storage.users),
                'notes_count': len(getattr(self.notes_manager, 'notes', {})),
                'messages_count': len(getattr(self.messaging_service, 'messages', {})),
                'password_history_count': len(getattr(self.password_history_manager, 'password_history', {}))
            }
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

    def _calculate_user_stats(self, company_id: str = None) -> Dict[str, Any]:
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
            if company_id and user_data.get('company_id') != company_id:
                continue
            stats['total_users'] += 1
            if user_data.get('verified'):
                stats['verified_users'] += 1
            if user_data.get('is_logged_in'):
                stats['logged_in_users'] += 1
            if user_data.get('is_owner'):
                stats['owners'] += 1
            for priv in user_data.get('privileges', []):
                stats['privilege_breakdown'][priv] = stats['privilege_breakdown'].get(priv, 0) + 1
            if not company_id:
                user_company = user_data.get('company_id', 'unknown')
                stats['company_breakdown'][user_company] = stats['company_breakdown'].get(user_company, 0) + 1
        return stats

    def _sanitize_user_data_for_export(self) -> Dict[str, Any]:
        sanitized = {}
        for email, user_data in self.storage.users.items():
            if isinstance(user_data, dict):
                sanitized_user = user_data.copy()
                for field in ['password', 'reset_token', 'verification_token']:
                    sanitized_user.pop(field, None)
                sanitized[email] = sanitized_user
        return sanitized

    def _sanitize_password_history_for_export(self) -> Dict[str, Any]:
        sanitized = {}
        password_history = getattr(self.password_history_manager, 'password_history', {})
        for user_uuid, history in password_history.items():
            if isinstance(history, list):
                sanitized[user_uuid] = [
                    {
                        'timestamp': entry.get('timestamp'),
                        'hash_length': len(entry.get('password_hash', ''))
                    }
                    for entry in history if isinstance(entry, dict)
                ]
        return sanitized

    def _safe_call(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {} if 'stats' in func.__name__ else None
"""
Main user storage class providing comprehensive user data management.
"""

import logging
from typing import Dict, List, Optional, Any
from .base_storage import BaseStorage
from .access_control import AccessControlMixin
from .file_handler import FileHandler

logger = logging.getLogger(__name__)


class UserStorage(BaseStorage, AccessControlMixin):
    """Main storage class for user data management with encryption and access control."""
    
    def __init__(self):
        """Initialize user storage with all required components."""
        BaseStorage.__init__(self)
        AccessControlMixin.__init__(self)
        
        # Initialize file handler
        self.file_handler = FileHandler()
        
        # Load all data
        self.users = self.file_handler.load_users()
        self.notes = self.file_handler.load_notes()
        self.messages = self.file_handler.load_messages()
    
    def _get_user(self, key, value):
        if not self.validate_input(value, str, key):
            return None
        for user in self.users.values():
            if isinstance(user, dict) and user.get(key) == value:
                return user
        return None

    def get_user_by_email(self, email):
        try:
            email = self.sanitize_email(email)
            return self.users.get(email) if email else None
        except Exception as e:
            logger.error(f"get_user_by_email: {type(e).__name__}: {e}")
            return None

    def get_user_by_uuid(self, uuid):
        try:
            return self._get_user('uuid', uuid)
        except Exception as e:
            logger.error(f"get_user_by_uuid: {type(e).__name__}: {e}")
            return None

    def get_all_users(self):
        try:
            return self.users.copy()
        except Exception as e:
            logger.error(f"get_all_users: {type(e).__name__}: {e}")
            return {}

    def save_user(self, user):
        try:
            if not isinstance(user, dict) or "email" not in user:
                return False
            email = self.sanitize_email(user["email"])
            if not email:
                return False
            user_copy = user.copy()
            user_copy["email"] = email
            self.users[email] = user_copy
            if self.file_handler.save_users(self.users):
                return True
            del self.users[email]
            return False
        except Exception as e:
            logger.error(f"save_user: {type(e).__name__}: {e}")
            return False

    def update_user(self, user):
        try:
            if not isinstance(user, dict) or "email" not in user:
                return False
            email = self.sanitize_email(user["email"])
            if not email or email not in self.users:
                return False
            original = self.users[email].copy()
            user_copy = user.copy()
            user_copy["email"] = email
            self.users[email] = user_copy
            if self.file_handler.save_users(self.users):
                return True
            self.users[email] = original
            return False
        except Exception as e:
            logger.error(f"update_user: {type(e).__name__}: {e}")
            return False

    def delete_user(self, email):
        try:
            email = self.sanitize_email(email)
            if not email or email not in self.users:
                return False
            user_data = self.users[email]
            user_uuid = user_data.get('uuid') if isinstance(user_data, dict) else None
            deleted_user = user_data.copy()
            del self.users[email]
            if not self.file_handler.save_users(self.users):
                self.users[email] = deleted_user
                return False
            if user_uuid:
                self.file_handler.cleanup_user_files(user_uuid, self.users, self.notes, self.messages)
            return True
        except Exception as e:
            logger.error(f"delete_user: {type(e).__name__}: {e}")
            return False

    def get_user_for_frontend(self, email, requesting_user_email=None):
        try:
            email = self.sanitize_email(email)
            requesting_user_email = self.sanitize_email(requesting_user_email) if requesting_user_email else None
            user = self.users.get(email)
            requesting_user = self.users.get(requesting_user_email) if requesting_user_email else None
            if not (email and user and requesting_user_email and requesting_user):
                return None
            if not self.can_access_user_data(requesting_user, user):
                return None
            is_own = (requesting_user_email == email)
            return self.get_filtered_user_data(user, requesting_user, is_own)
        except Exception as e:
            logger.error(f"get_user_for_frontend: {type(e).__name__}: {e}")
            return None

    def get_users_by_company(self, company_id, requesting_user_email=None):
        try:
            if not self.validate_input(company_id, str, "company_id"):
                return []
            requesting_user_email = self.sanitize_email(requesting_user_email) if requesting_user_email else None
            requesting_user = self.users.get(requesting_user_email) if requesting_user_email else None
            if not (requesting_user_email and requesting_user and self.validate_company_access(requesting_user, company_id)):
                return []
            company_users = [u for u in self.users.values() if isinstance(u, dict) and u.get('company_id') == company_id]
            return self.filter_company_users(company_users, requesting_user)
        except Exception as e:
            logger.error(f"get_users_by_company: {type(e).__name__}: {e}")
            return []

    def _get_user_data(self, user_uuid, requesting_user_email, data_type):
        try:
            if not self.validate_input(user_uuid, str, "user_uuid"):
                return None
            requesting_user_email = self.sanitize_email(requesting_user_email)
            requesting_user = self.users.get(requesting_user_email)
            target_user = self.get_user_by_uuid(user_uuid)
            if not (requesting_user_email and requesting_user and target_user):
                return None
            if not self.can_access_user_data(requesting_user, target_user):
                return None
            return getattr(self, data_type).get(user_uuid, {})
        except Exception as e:
            logger.error(f"_get_user_data: {type(e).__name__}: {e}")
            return None

    def get_user_notes(self, user_uuid, requesting_user_email):
        return self._get_user_data(user_uuid, requesting_user_email, 'notes')

    def get_user_messages(self, user_uuid, requesting_user_email):
        return self._get_user_data(user_uuid, requesting_user_email, 'messages')

    def _save_user_data(self, user_uuid, data, requesting_user_email, data_type):
        try:
            if not self.validate_input(user_uuid, str, "user_uuid") or not isinstance(data, dict):
                return False
            requesting_user_email = self.sanitize_email(requesting_user_email)
            requesting_user = self.users.get(requesting_user_email)
            target_user = self.get_user_by_uuid(user_uuid)
            if not (requesting_user_email and requesting_user and target_user):
                return False
            if requesting_user.get('uuid') != user_uuid and not self.has_privilege(requesting_user.get('privileges', []), 'user_management'):
                return False
            getattr(self, data_type)[user_uuid] = data
            save_func = getattr(self.file_handler, f'save_{data_type}')
            if save_func(getattr(self, data_type)):
                return True
            del getattr(self, data_type)[user_uuid]
            return False
        except Exception as e:
            logger.error(f"_save_user_data: {type(e).__name__}: {e}")
            return False

    def save_user_notes(self, user_uuid, notes, requesting_user_email):
        return self._save_user_data(user_uuid, notes, requesting_user_email, 'notes')

    def save_user_messages(self, user_uuid, messages, requesting_user_email):
        return self._save_user_data(user_uuid, messages, requesting_user_email, 'messages')

    def get_storage_stats(self):
        try:
            file_stats = self.file_handler.get_file_stats()
            return {
                'users_count': len(self.users),
                'notes_count': len(self.notes),
                'messages_count': len(self.messages),
                'file_stats': file_stats,
                'memory_usage': {
                    'users_keys': list(self.users.keys())[:5],
                    'notes_keys': list(self.notes.keys())[:5],
                    'messages_keys': list(self.messages.keys())[:5]
                }
            }
        except Exception as e:
            logger.error(f"get_storage_stats: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'users_count': 0,
                'notes_count': 0,
                'messages_count': 0
            }
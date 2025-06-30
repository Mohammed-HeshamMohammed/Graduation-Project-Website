import logging
from typing import List, Dict, Any, Optional, Tuple
from app.services.storage import UserStorage
from app.services.notes import NotesManager
from app.services.Password_History.managers import PasswordHistoryManager
from app.services.messaging import MessagingService

from .validators import UserValidator
from .privilege_manager import PrivilegeManager
from .data_manager import DataManager
from .auth_utils import AuthUtils

# Configure logging
logger = logging.getLogger(__name__)


class UserUtils:
    """Main utility class for user management operations"""
    
    def __init__(self, storage: UserStorage = None):
        """Initialize utils with storage instance"""
        try:
            self.storage = storage or UserStorage()
            self.notes_manager = NotesManager(self.storage)
            self.messaging_service = MessagingService()
            self.validator = UserValidator()
            self.privilege_manager = PrivilegeManager(self.storage)
            self.password_history_manager = PasswordHistoryManager.get_instance(self.storage)
            self.data_manager = DataManager(
                self.storage, self.notes_manager, 
                self.password_history_manager, 
                self.messaging_service
            )
        except Exception as e:
            logger.error(f"UserUtils initialization failed: {e}")
            raise

    def get_all_users(self) -> Dict[str, Any]:
        """Get all users (for admin purposes only)"""
        return self.storage.get_all_users()

    def get_user_count(self) -> int:
        """Get the total number of users"""
        return len(self.storage.users)

    def user_exists(self, email: str) -> bool:
        """Check if a user exists"""
        try:
            if not email or not isinstance(email, str):
                return False
            return self.storage.get_user_by_email(email) is not None
        except Exception as e:
            logger.error(f"User existence check failed: {e}")
            return False

    def get_company_user_count(self, company_id: str) -> int:
        """Get the number of users in a specific company"""
        try:
            if not company_id or not isinstance(company_id, str):
                return 0
            return sum(1 for user_data in self.storage.users.values()
                       if isinstance(user_data, dict) and user_data.get('company_id') == company_id)
        except Exception as e:
            logger.error(f"Company user count failed: {e}")
            return 0

    def search_users_by_company(self, company_id: str, search_term: str = "",
                               requesting_user_email: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for users within a specific company"""
        try:
            if not all([company_id, isinstance(company_id, str), requesting_user_email]):
                return []
            
            requesting_user = self.storage.get_user_by_email(requesting_user_email)
            if not (requesting_user and requesting_user.get('company_id') == company_id):
                return []
            
            search_term = search_term.lower().strip() if search_term else ""
            matching_users = []
            
            for email, user_data in self.storage.users.items():
                if not (isinstance(user_data, dict) and user_data.get('company_id') == company_id):
                    continue
                
                if search_term and not self._matches_search_term(user_data, search_term):
                    continue
                
                is_own_data = (email == requesting_user_email)
                filtered_user = self.storage.get_filtered_user_data(
                    user_data, requesting_user, is_own_data
                )
                matching_users.append(filtered_user)
                
                if len(matching_users) >= limit:
                    break
            
            return matching_users
        except Exception as e:
            logger.error(f"User search failed: {e}")
            return []

    def _matches_search_term(self, user_data: Dict[str, Any], search_term: str) -> bool:
        """Check if user data matches the search term"""
        try:
            searchable_fields = [
                user_data.get('email', ''),
                user_data.get('full_name', ''),
                user_data.get('uuid', ''),
                ' '.join(user_data.get('privileges', []))
            ]
            return any(search_term in str(field).lower() for field in searchable_fields if field)
        except Exception as e:
            logger.error(f"Search term matching failed: {e}")
            return False

    # Delegate to privilege manager
    def has_privilege(self, user_privileges: List[str], required_privilege: str) -> bool:
        """Check if user has a specific privilege or higher"""
        return self.privilege_manager.has_privilege(user_privileges, required_privilege)

    def can_access_feature(self, user_privileges: List[str], feature: str) -> bool:
        """Check if user can access a specific feature based on privilege hierarchy"""
        return self.privilege_manager.can_access_feature(user_privileges, feature)

    # Delegate to validator
    def validate_user_data(self, user_data: dict) -> Tuple[bool, str]:
        """Validate user data structure according to schema"""
        return self.validator.validate_user_data(user_data)

    # Delegate to data manager
    def backup_data(self, backup_path: str = None) -> bool:
        """Create a manual backup of all data"""
        return self.data_manager.backup_data(backup_path)

    def get_user_statistics(self, company_id: str = None) -> Dict[str, Any]:
        """Get user statistics, optionally filtered by company"""
        return self.data_manager.get_user_statistics(company_id)

    def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        """Clean up old messages and notes (for maintenance)"""
        return self.data_manager.cleanup_old_data(days_old)

    # Helper method for handling user notes operations
    def _handle_user_notes(self, action: str, **kwargs) -> Any:
        """Handle various note operations with error handling"""
        actions = {
            'add': self.notes_manager.add_user_note,
            'get': self.storage.get_user_notes,
            'update': self.notes_manager.update_note,
            'delete': self.notes_manager.delete_note,
            'search': self.notes_manager.search_notes,
            'save': self.storage.save_user_notes
        }
        try:
            return actions[action](**kwargs)
        except Exception as e:
            logger.error(f"Note action '{action}' failed: {e}")
            return False if action in ['add', 'update', 'delete', 'save'] else None

    # Notes management methods
    def add_user_note(self, user_uuid: str, note: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Add a note for a user"""
        return self._handle_user_notes('add', user_uuid=user_uuid, note=note, 
                                      author_uuid=author_uuid, author_privileges=author_privileges)

    def get_user_notes(self, user_uuid: str, requesting_user_email: str) -> Optional[Dict[str, Any]]:
        """Get notes for a user"""
        return self._handle_user_notes('get', user_uuid=user_uuid, requesting_user_email=requesting_user_email)

    def update_note(self, note_id: str, new_content: str, user_uuid: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Update an existing note"""
        return self._handle_user_notes('update', note_id=note_id, new_content=new_content, 
                                      user_uuid=user_uuid, author_uuid=author_uuid, author_privileges=author_privileges)

    def delete_note(self, note_id: str, user_uuid: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Delete a note"""
        return self._handle_user_notes('delete', note_id=note_id, user_uuid=user_uuid, 
                                      author_uuid=author_uuid, author_privileges=author_privileges)

    def search_notes(self, search_term: str, company_id: str, requesting_user_privileges: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search notes within a company"""
        return self._handle_user_notes('search', search_term=search_term, company_id=company_id, 
                                      requesting_user_privileges=requesting_user_privileges, limit=limit)

    def save_user_notes(self, user_uuid: str, notes: Dict[str, Any], requesting_user_email: str) -> bool:
        """Save user notes"""
        return self._handle_user_notes('save', user_uuid=user_uuid, notes=notes, requesting_user_email=requesting_user_email)

    # Helper method for handling password history operations
    def _handle_password_history(self, action: str, **kwargs) -> Any:
        """Handle various password history operations with error handling"""
        actions = {
            'check': self.password_history_manager.check_password_in_history,
            'update': self.password_history_manager.update_user_password,
            'count': self.password_history_manager.get_password_history_count,
            'clear': self.password_history_manager.clear_user_history,
            'add': self.password_history_manager.add_password_to_history,
            'transfer': self.password_history_manager.handle_user_company_transfer
        }
        try:
            return actions[action](**kwargs)
        except Exception as e:
            logger.error(f"Password history action '{action}' failed: {e}")
            return False if action in ['update', 'clear', 'add', 'transfer'] else 0 if action == 'count' else False

    # Password history management methods
    def check_password_in_history(self, user_uuid: str, password_hash: str, **kwargs) -> bool:
        """Check if password was used before"""
        return self._handle_password_history('check', user_uuid=user_uuid, password_hash=password_hash, **kwargs)

    def update_user_password(self, user_uuid: str, company_uuid: str, new_password_hash: str, 
                           bypass_history_check: bool = False, **kwargs) -> bool:
        """Update user password and add to history"""
        return self._handle_password_history('update', user_uuid=user_uuid, company_uuid=company_uuid, 
                                           new_password_hash=new_password_hash, bypass_history_check=bypass_history_check, **kwargs)

    def get_password_history_count(self, user_uuid: str, **kwargs) -> int:
        """Get the number of passwords in history for a user"""
        return self._handle_password_history('count', user_uuid=user_uuid, **kwargs)

    def clear_user_password_history(self, user_uuid: str, company_uuid: str, requesting_admin_uuid: str, **kwargs) -> bool:
        """Clear password history for a specific user"""
        return self._handle_password_history('clear', user_uuid=user_uuid, company_uuid=company_uuid, 
                                           requesting_admin_uuid=requesting_admin_uuid, **kwargs)

    def add_password_to_history(self, user_uuid: str, company_uuid: str, password_hash: str, max_history: int = None, **kwargs) -> bool:
        """Add password to history"""
        return self._handle_password_history('add', user_uuid=user_uuid, company_uuid=company_uuid, 
                                           password_hash=password_hash, max_history=max_history, **kwargs)

    def handle_user_company_transfer(self, user_uuid: str, old_company_uuid: str, new_company_uuid: str, 
                                   requesting_admin_uuid: str, preserve_history: bool = True, **kwargs) -> bool:
        """Handle user company transfer"""
        return self._handle_password_history('transfer', user_uuid=user_uuid, old_company_uuid=old_company_uuid, 
                                           new_company_uuid=new_company_uuid, requesting_admin_uuid=requesting_admin_uuid, 
                                           preserve_history=preserve_history, **kwargs)

    # Helper method for handling messaging operations
    def _handle_messaging(self, action: str, **kwargs) -> Any:
        """Handle various messaging operations with error handling"""
        actions = {
            'add': self.messaging_service.add_user_message,
            'get': self.storage.get_user_messages,
            'warning': self.messaging_service.send_warning_to_subordinates,
            'disciplinary': self.messaging_service.send_disciplinary_action,
            'cleanup': self.messaging_service.cleanup_user_messages,
            'save': self.storage.save_user_messages
        }
        try:
            return actions[action](**kwargs)
        except Exception as e:
            logger.error(f"Messaging action '{action}' failed: {e}")
            return False if action in ['add', 'cleanup', 'save'] else {} if action in ['warning', 'disciplinary'] else None

    # Messaging methods
    def add_message_to_user(self, user_uuid: str, message: str, author_uuid: str, message_type: str = "general") -> bool:
        """Add a message for a user"""
        return self._handle_messaging('add', user_uuid=user_uuid, message=message, author_uuid=author_uuid, message_type=message_type)

    def get_user_messages(self, user_uuid: str, requesting_user_email: str) -> Optional[Dict[str, Any]]:
        """Get messages for a user"""
        return self._handle_messaging('get', user_uuid=user_uuid, requesting_user_email=requesting_user_email)

    def send_warning_to_subordinates(self, sender_uuid: str, message: str, target_user_uuids: List[str] = None) -> Dict[str, Any]:
        """Send warning messages to subordinates"""
        return self._handle_messaging('warning', sender_uuid=sender_uuid, message=message, target_user_uuids=target_user_uuids)

    def send_disciplinary_action(self, sender_uuid: str, target_user_uuid: str, action_type: str, 
                               message: str, severity: str = "medium") -> Dict[str, Any]:
        """Send disciplinary action messages"""
        return self._handle_messaging('disciplinary', sender_uuid=sender_uuid, target_user_uuid=target_user_uuid, 
                                    action_type=action_type, message=message, severity=severity)

    def cleanup_user_messages(self, user_uuid: str) -> bool:
        """Clean up messages for a deleted user"""
        return self._handle_messaging('cleanup', user_uuid=user_uuid)

    def save_user_messages(self, user_uuid: str, messages: Dict[str, Any], requesting_user_email: str) -> bool:
        """Save user messages"""
        return self._handle_messaging('save', user_uuid=user_uuid, messages=messages, requesting_user_email=requesting_user_email)

    # Static methods for authentication utilities
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return AuthUtils.hash_password(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return AuthUtils.verify_password(plain_password, hashed_password)

    @staticmethod
    def create_token(data: dict, expires_minutes: int = None) -> str:
        """Create a JWT token"""
        return AuthUtils.create_token(data, expires_minutes)

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify a JWT token"""
        return AuthUtils.verify_token(token)

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a verification token"""
        return AuthUtils.generate_verification_token()

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password strength"""
        return AuthUtils.validate_password_strength(password)
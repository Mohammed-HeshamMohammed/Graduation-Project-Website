import logging
from typing import List, Dict, Any, Optional
from app.services.storage import UserStorage
from app.services.notes import NotesManager
from app.services.Password_History.models import PasswordHistoryManager
from app.services.messaging import MessagingService

from .validators import UserValidator
from .privilege_manager import PrivilegeManager
from .data_manager import DataManager

# Configure logging
logger = logging.getLogger(__name__)


class UserUtils:
    """Main utility class for user management operations"""
    
    def __init__(self, storage: UserStorage):
        """Initialize utils with storage instance"""
        self.storage = storage
        self.notes_manager = NotesManager(storage)
        self.password_history_manager = PasswordHistoryManager(storage)
        self.messaging_service = MessagingService()
        
        # Initialize sub-managers
        self.validator = UserValidator()
        self.privilege_manager = PrivilegeManager(storage)
        self.data_manager = DataManager(
            storage, 
            self.notes_manager, 
            self.password_history_manager, 
            self.messaging_service
        )
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users (for admin purposes only)"""
        return self.storage.users.copy()

    def get_user_count(self) -> int:
        """Get the total number of users"""
        return len(self.storage.users)

    def user_exists(self, email: str) -> bool:
        """Check if a user exists"""
        if not email or not isinstance(email, str):
            return False
        return email.lower().strip() in self.storage.users

    def get_company_user_count(self, company_id: str) -> int:
        """Get the number of users in a specific company"""
        try:
            if not company_id or not isinstance(company_id, str):
                return 0
            
            count = sum(1 for user_data in self.storage.users.values() 
                       if isinstance(user_data, dict) and user_data.get('company_id') == company_id)
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting company user count: {type(e).__name__}: {e}")
            return 0

    def search_users_by_company(self, company_id: str, search_term: str = "", 
                               requesting_user_email: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for users within a specific company"""
        try:
            if not company_id or not isinstance(company_id, str):
                logger.warning("Invalid company_id provided to search_users_by_company")
                return []
            
            if not requesting_user_email:
                logger.warning("No requesting user provided to search_users_by_company")
                return []
            
            requesting_user = self.storage.users.get(requesting_user_email.lower().strip())
            if not requesting_user or not isinstance(requesting_user, dict):
                logger.warning(f"Invalid requesting user: {requesting_user_email}")
                return []
            
            # Check if requesting user belongs to the company
            if requesting_user.get('company_id') != company_id:
                logger.warning(f"User {requesting_user_email} cannot search company {company_id}")
                return []
            
            search_term = search_term.lower().strip() if search_term else ""
            matching_users = []
            
            for email, user_data in self.storage.users.items():
                if (isinstance(user_data, dict) and 
                    user_data.get('company_id') == company_id):
                
                    # If no search term, include all company users
                    include_user = True
                    if search_term:
                        # Search in various fields
                        searchable_fields = [
                            user_data.get('email', ''),
                            user_data.get('full_name', ''),
                            user_data.get('uuid', ''),
                            ' '.join(user_data.get('privileges', []))
                        ]
                        
                        # Check if search term matches any field
                        include_user = any(search_term in str(field).lower() 
                                         for field in searchable_fields if field)
                    
                    if include_user:
                        if email == requesting_user_email:
                            # Own data
                            user_copy = self.storage._get_own_user_data(user_data.copy())
                        else:
                            # Colleague data
                            user_copy = self.storage._get_company_colleague_data(user_data.copy(), requesting_user)
                        
                        matching_users.append(user_copy)
                    
                    # Apply limit
                    if len(matching_users) >= limit:
                        break
            
            logger.info(f"Found {len(matching_users)} matching users for company {company_id}")
            return matching_users
            
        except Exception as e:
            logger.error(f"Error searching users by company: {type(e).__name__}: {e}")
            return []

    # Delegate to privilege manager
    def has_privilege(self, user_privileges: List[str], required_privilege: str) -> bool:
        """Check if user has a specific privilege or higher"""
        return self.privilege_manager.has_privilege(user_privileges, required_privilege)

    def can_access_feature(self, user_privileges: List[str], feature: str) -> bool:
        """Check if user can access a specific feature based on privilege hierarchy"""
        return self.privilege_manager.can_access_feature(user_privileges, feature)

    # Delegate to validator
    def validate_user_data(self, user_data: dict) -> tuple[bool, str]:
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

    # Notes management methods
    def add_user_note(self, user_uuid: str, note: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Add a note for a user"""
        return self.notes_manager.add_user_note(user_uuid, note, author_uuid, author_privileges)

    def get_user_notes(self, user_uuid: str, requesting_user_uuid: str, requesting_user_privileges: List[str]) -> List[Dict[str, Any]]:
        """Get notes for a user"""
        return self.notes_manager.get_user_notes(user_uuid, requesting_user_uuid, requesting_user_privileges)

    def update_note(self, note_id: str, new_content: str, user_uuid: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Update an existing note"""
        return self.notes_manager.update_note(note_id, new_content, user_uuid, author_uuid, author_privileges)

    def delete_note(self, note_id: str, user_uuid: str, author_uuid: str, author_privileges: List[str]) -> bool:
        """Delete a note"""
        return self.notes_manager.delete_note(note_id, user_uuid, author_uuid, author_privileges)

    def search_notes(self, search_term: str, company_id: str, requesting_user_privileges: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search notes within a company"""
        return self.notes_manager.search_notes(search_term, company_id, requesting_user_privileges, limit)

    # Password history management methods
    def check_password_in_history(self, user_uuid: str, password_hash: str) -> bool:
        """Check if password was used before"""
        return self.password_history_manager.check_password_in_history(user_uuid, password_hash)

    def update_user_password(self, user_uuid: str, new_password_hash: str) -> bool:
        """Update user password and add to history"""
        return self.password_history_manager.update_user_password(user_uuid, new_password_hash)

    def get_password_history_count(self, user_uuid: str) -> int:
        """Get the number of passwords in history for a user"""
        return self.password_history_manager.get_password_history_count(user_uuid)

    def clear_user_password_history(self, user_uuid: str) -> bool:
        """Clear password history for a specific user"""
        return self.password_history_manager.clear_user_password_history(user_uuid)

    # Messaging methods
    def add_message_to_user(self, user_uuid: str, message: str, author_uuid: str, message_type: str = "general") -> bool:
        """Add a message for a user"""
        return self.messaging_service.add_user_message(user_uuid, message, author_uuid, message_type)

    def get_user_messages(self, user_uuid: str, requesting_user_uuid: str, requesting_user_privileges: List[str]) -> List[Dict[str, Any]]:
        """Get messages for a user"""
        return self.messaging_service.get_user_messages(user_uuid, requesting_user_uuid, requesting_user_privileges)

    def send_warning_to_subordinates(self, sender_uuid: str, message: str, target_user_uuids: List[str] = None) -> Dict[str, Any]:
        """Send warning messages to subordinates"""
        return self.messaging_service.send_warning_to_subordinates(sender_uuid, message, target_user_uuids)

    def send_disciplinary_action(self, sender_uuid: str, target_user_uuid: str, action_type: str, message: str, severity: str = "medium") -> Dict[str, Any]:
        """Send disciplinary action messages"""
        return self.messaging_service.send_disciplinary_action(sender_uuid, target_user_uuid, action_type, message, severity)

    def cleanup_user_messages(self, user_uuid: str) -> bool:
        """Clean up messages for a deleted user"""
        return self.messaging_service.cleanup_user_messages(user_uuid)
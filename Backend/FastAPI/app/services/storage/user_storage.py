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
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email with input validation.
        
        Args:
            email: Email address to search for
            
        Returns:
            User data dictionary or None if not found
        """
        sanitized_email = self.sanitize_email(email)
        if not sanitized_email:
            return None
        
        return self.users.get(sanitized_email)
    
    def get_user_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by UUID.
        
        Args:
            uuid: UUID to search for
            
        Returns:
            User data dictionary or None if not found
        """
        if not self.validate_input(uuid, str, "UUID"):
            return None
        
        for user_data in self.users.values():
            if isinstance(user_data, dict) and user_data.get('uuid') == uuid:
                return user_data
        return None
    
    def get_all_users(self) -> Dict[str, Any]:
        """
        Get all users (for admin purposes only).
        
        Returns:
            Copy of all user data
        """
        return self.users.copy()
    
    def save_user(self, user: Dict[str, Any]) -> bool:
        """
        Save a new user with validation.
        
        Args:
            user: User data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate user data structure
            if not isinstance(user, dict) or "email" not in user:
                logger.error("Invalid user data provided to save_user")
                return False
            
            email = self.sanitize_email(user["email"])
            if not email:
                logger.error("Invalid email provided to save_user")
                return False
            
            # Create a copy to avoid modifying the original
            user_copy = user.copy()
            user_copy["email"] = email
            
            # Save to memory
            self.users[email] = user_copy
            
            # Persist to file
            success = self.file_handler.save_users(self.users)
            
            if success:
                logger.info(f"Successfully saved user: {email}")
            else:
                logger.error(f"Failed to save user: {email}")
                # Rollback memory change on file save failure
                if email in self.users:
                    del self.users[email]
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving user: {type(e).__name__}: {e}")
            return False
    
    def update_user(self, user: Dict[str, Any]) -> bool:
        """
        Update an existing user with validation.
        
        Args:
            user: Updated user data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate user data structure
            if not isinstance(user, dict) or "email" not in user:
                logger.error("Invalid user data provided to update_user")
                return False
            
            email = self.sanitize_email(user["email"])
            if not email:
                logger.error("Invalid email provided to update_user")
                return False
            
            if email not in self.users:
                logger.warning(f"Attempted to update non-existent user: {email}")
                return False
            
            # Store original data for rollback
            original_user = self.users[email].copy()
            
            # Create a copy to avoid modifying the original
            user_copy = user.copy()
            user_copy["email"] = email
            
            # Update in memory
            self.users[email] = user_copy
            
            # Persist to file
            success = self.file_handler.save_users(self.users)
            
            if success:
                logger.info(f"Successfully updated user: {email}")
            else:
                logger.error(f"Failed to update user: {email}")
                # Rollback memory change on file save failure
                self.users[email] = original_user
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating user: {type(e).__name__}: {e}")
            return False
    
    def delete_user(self, email: str) -> bool:
        """
        Delete a user with validation and cleanup.
        
        Args:
            email: Email of user to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            email = self.sanitize_email(email)
            if not email:
                logger.warning("Invalid email provided to delete_user")
                return False
            
            if email not in self.users:
                logger.warning(f"Attempted to delete non-existent user: {email}")
                return False
            
            # Get user data before deletion
            user_data = self.users[email]
            user_uuid = user_data.get('uuid') if isinstance(user_data, dict) else None
            
            # Store for rollback
            deleted_user = user_data.copy()
            
            # Delete from memory
            del self.users[email]
            
            # Save users file
            success = self.file_handler.save_users(self.users)
            
            if not success:
                logger.error(f"Failed to save users after deletion: {email}")
                # Rollback
                self.users[email] = deleted_user
                return False
            
            # Clean up related data
            if user_uuid:
                cleanup_success = self.file_handler.cleanup_user_files(
                    user_uuid, self.users, self.notes, self.messages
                )
                if not cleanup_success:
                    logger.warning(f"User deleted but cleanup partially failed: {email}")
            
            logger.info(f"Successfully deleted user: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {type(e).__name__}: {e}")
            return False
    
    def get_user_for_frontend(self, email: str, requesting_user_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get user data for frontend with proper security filtering.
        
        Args:
            email: Email of user to get data for
            requesting_user_email: Email of user making the request
            
        Returns:
            Filtered user data or None if access denied
        """
        try:
            email = self.sanitize_email(email)
            if not email:
                logger.warning("Invalid email provided to get_user_for_frontend")
                return None
            
            user = self.users.get(email)
            if not user or not isinstance(user, dict):
                logger.info(f"User not found for frontend request: {email}")
                return None
            
            # If no requesting user (unauthenticated), return nothing
            if not requesting_user_email:
                logger.info(f"Unauthenticated request for user data: {email}")
                return None
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                logger.warning("Invalid requesting user email")
                return None
            
            requesting_user = self.users.get(requesting_user_email)
            
            if not requesting_user or not isinstance(requesting_user, dict):
                logger.warning(f"Invalid requesting user: {requesting_user_email}")
                return None
            
            # Check access permissions
            if not self.can_access_user_data(requesting_user, user):
                logger.info(f"Access denied: {requesting_user_email} cannot access {email}")
                return None
            
            # Filter data based on access level
            is_own_data = (requesting_user_email == email)
            return self.get_filtered_user_data(user, requesting_user, is_own_data)
            
        except Exception as e:
            logger.error(f"Error getting user data for frontend: {type(e).__name__}: {e}")
            return None
    
    def get_users_by_company(self, company_id: str, requesting_user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all users in a company with proper access control.
        
        Args:
            company_id: Company ID to get users for
            requesting_user_email: Email of user making the request
            
        Returns:
            List of filtered user data dictionaries
        """
        try:
            if not self.validate_input(company_id, str, "company_id"):
                return []
            
            if not requesting_user_email:
                logger.warning("No requesting user provided to get_users_by_company")
                return []
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                return []
            
            requesting_user = self.users.get(requesting_user_email)
            if not requesting_user or not isinstance(requesting_user, dict):
                logger.warning(f"Invalid requesting user: {requesting_user_email}")
                return []
            
            # Validate company access
            if not self.validate_company_access(requesting_user, company_id):
                return []
            
            # Collect users from the company
            company_users = []
            for email, user_data in self.users.items():
                if (isinstance(user_data, dict) and 
                    user_data.get('company_id') == company_id):
                    company_users.append(user_data)
            
            # Filter users based on access level
            filtered_users = self.filter_company_users(company_users, requesting_user)
            
            logger.info(f"Found {len(filtered_users)} users for company {company_id}")
            return filtered_users
            
        except Exception as e:
            logger.error(f"Error getting users by company: {type(e).__name__}: {e}")
            return []
    
    def get_user_notes(self, user_uuid: str, requesting_user_email: str) -> Optional[Dict[str, Any]]:
        """
        Get notes for a user with access control.
        
        Args:
            user_uuid: UUID of user whose notes to get
            requesting_user_email: Email of user making the request
            
        Returns:
            User notes or None if access denied
        """
        try:
            if not self.validate_input(user_uuid, str, "user_uuid"):
                return None
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                return None
            
            requesting_user = self.users.get(requesting_user_email)
            if not requesting_user:
                return None
            
            target_user = self.get_user_by_uuid(user_uuid)
            if not target_user:
                return None
            
            # Check access permissions
            if not self.can_access_user_data(requesting_user, target_user):
                logger.info(f"Access denied for notes: {requesting_user_email} -> {user_uuid}")
                return None
            
            return self.notes.get(user_uuid, {})
            
        except Exception as e:
            logger.error(f"Error getting user notes: {type(e).__name__}: {e}")
            return None
    
    def save_user_notes(self, user_uuid: str, notes: Dict[str, Any], requesting_user_email: str) -> bool:
        """
        Save notes for a user with access control.
        
        Args:
            user_uuid: UUID of user whose notes to save
            notes: Notes data to save
            requesting_user_email: Email of user making the request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.validate_input(user_uuid, str, "user_uuid"):
                return False
            
            if not isinstance(notes, dict):
                logger.error("Invalid notes data provided")
                return False
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                return False
            
            requesting_user = self.users.get(requesting_user_email)
            if not requesting_user:
                return False
            
            target_user = self.get_user_by_uuid(user_uuid)
            if not target_user:
                logger.warning(f"Target user not found: {user_uuid}")
                return False
            
            # Check access permissions (only own notes or admin access)
            if (requesting_user.get('uuid') != user_uuid and 
                not self.has_privilege(requesting_user.get('privileges', []), 'user_management')):
                logger.info(f"Access denied for saving notes: {requesting_user_email} -> {user_uuid}")
                return False
            
            # Save to memory
            self.notes[user_uuid] = notes
            
            # Persist to file
            success = self.file_handler.save_notes(self.notes)
            
            if success:
                logger.info(f"Successfully saved notes for user: {user_uuid}")
            else:
                logger.error(f"Failed to save notes for user: {user_uuid}")
                # Rollback on failure
                if user_uuid in self.notes:
                    del self.notes[user_uuid]
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving user notes: {type(e).__name__}: {e}")
            return False
    
    def get_user_messages(self, user_uuid: str, requesting_user_email: str) -> Optional[Dict[str, Any]]:
        """
        Get messages for a user with access control.
        
        Args:
            user_uuid: UUID of user whose messages to get
            requesting_user_email: Email of user making the request
            
        Returns:
            User messages or None if access denied
        """
        try:
            if not self.validate_input(user_uuid, str, "user_uuid"):
                return None
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                return None
            
            requesting_user = self.users.get(requesting_user_email)
            if not requesting_user:
                return None
            
            target_user = self.get_user_by_uuid(user_uuid)
            if not target_user:
                return None
            
            # Check access permissions
            if not self.can_access_user_data(requesting_user, target_user):
                logger.info(f"Access denied for messages: {requesting_user_email} -> {user_uuid}")
                return None
            
            return self.messages.get(user_uuid, {})
            
        except Exception as e:
            logger.error(f"Error getting user messages: {type(e).__name__}: {e}")
            return None
    
    def save_user_messages(self, user_uuid: str, messages: Dict[str, Any], requesting_user_email: str) -> bool:
        """
        Save messages for a user with access control.
        
        Args:
            user_uuid: UUID of user whose messages to save
            messages: Messages data to save
            requesting_user_email: Email of user making the request
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.validate_input(user_uuid, str, "user_uuid"):
                return False
            
            if not isinstance(messages, dict):
                logger.error("Invalid messages data provided")
                return False
            
            requesting_user_email = self.sanitize_email(requesting_user_email)
            if not requesting_user_email:
                return False
            
            requesting_user = self.users.get(requesting_user_email)
            if not requesting_user:
                return False
            
            target_user = self.get_user_by_uuid(user_uuid)
            if not target_user:
                logger.warning(f"Target user not found: {user_uuid}")
                return False
            
            # Check access permissions (only own messages or admin access)
            if (requesting_user.get('uuid') != user_uuid and 
                not self.has_privilege(requesting_user.get('privileges', []), 'user_management')):
                logger.info(f"Access denied for saving messages: {requesting_user_email} -> {user_uuid}")
                return False
            
            # Save to memory
            self.messages[user_uuid] = messages
            
            # Persist to file
            success = self.file_handler.save_messages(self.messages)
            
            if success:
                logger.info(f"Successfully saved messages for user: {user_uuid}")
            else:
                logger.error(f"Failed to save messages for user: {user_uuid}")
                # Rollback on failure
                if user_uuid in self.messages:
                    del self.messages[user_uuid]
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving user messages: {type(e).__name__}: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics and health information.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            file_stats = self.file_handler.get_file_stats()
            
            return {
                'users_count': len(self.users),
                'notes_count': len(self.notes),
                'messages_count': len(self.messages),
                'file_stats': file_stats,
                'memory_usage': {
                    'users_keys': list(self.users.keys())[:5],  # Sample for debugging
                    'notes_keys': list(self.notes.keys())[:5],
                    'messages_keys': list(self.messages.keys())[:5]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'users_count': 0,
                'notes_count': 0,
                'messages_count': 0
            }
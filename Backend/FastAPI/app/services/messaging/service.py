"""
Main Messaging Service Module

Provides the main MessagingService class that orchestrates all messaging functionality.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.services.storage import UserStorage
from .storage import MessageStorage
from .access_control import MessageAccessControl
from .disciplinary import DisciplinaryActionManager
from .statistics import MessageStatistics
from .cleanup import MessageCleanup

logger = logging.getLogger(__name__)


class MessagingService:
    """Main messaging service that orchestrates all messaging functionality"""
    
    def __init__(self):
        """Initialize messaging service with all components"""
        # Initialize storage
        self.storage = MessageStorage()
        self.user_storage = UserStorage()
        
        # Initialize access control
        self.access_control = MessageAccessControl()
        
        # Load messages
        self.messages = self.storage.load_messages()
        
        # Initialize components with required dependencies
        self.disciplinary_manager = DisciplinaryActionManager(
            self.user_storage, 
            self._add_message_internal
        )
        self.statistics = MessageStatistics(self.user_storage)
        self.cleanup = MessageCleanup(self._save_messages_internal)
    
    def add_user_message(self, user_uuid: str, message: str, author_uuid: str, 
                        message_type: str = "general") -> bool:
        """Add a message for a user
        
        Args:
            user_uuid: UUID of the user receiving the message
            message: Message content
            author_uuid: UUID of the message author
            message_type: Type of message (general, warning, info, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        return self._add_message_internal(user_uuid, message, author_uuid, message_type)
    
    def get_user_messages(self, user_uuid: str, requesting_user_uuid: str, 
                         requesting_user_privileges: List[str]) -> List[Dict[str, Any]]:
        """Get messages for a user with access control
        
        Args:
            user_uuid: UUID of the user whose messages to retrieve
            requesting_user_uuid: UUID of the user making the request
            requesting_user_privileges: List of privileges for the requesting user
            
        Returns:
            List of messages for the user
        """
        try:
            # Check access permissions
            if not self.access_control.can_access_user_messages(
                user_uuid, requesting_user_uuid, requesting_user_privileges
            ):
                return []
            
            return self.messages.get(user_uuid, [])
            
        except Exception as e:
            logger.error(f"Error getting user messages: {type(e).__name__}: {e}")
            return []
    
    def mark_message_as_read(self, user_uuid: str, message_id: str) -> bool:
        """Mark a message as read
        
        Args:
            user_uuid: UUID of the user
            message_id: ID of the message to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_uuid in self.messages:
                for message in self.messages[user_uuid]:
                    if message.get('id') == message_id:
                        message['read'] = True
                        return self._save_messages_internal(self.messages)
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking message as read: {type(e).__name__}: {e}")
            return False
    
    def delete_message(self, user_uuid: str, message_id: str, requesting_user_uuid: str, 
                      requesting_user_privileges: List[str]) -> bool:
        """Delete a message with proper access control
        
        Args:
            user_uuid: UUID of the user whose message to delete
            message_id: ID of the message to delete
            requesting_user_uuid: UUID of the user making the request
            requesting_user_privileges: List of privileges for the requesting user
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check permissions
            if not self.access_control.can_delete_message(
                user_uuid, requesting_user_uuid, requesting_user_privileges
            ):
                return False
            
            if user_uuid in self.messages:
                original_count = len(self.messages[user_uuid])
                self.messages[user_uuid] = [
                    msg for msg in self.messages[user_uuid] 
                    if msg.get('id') != message_id
                ]
                
                if len(self.messages[user_uuid]) < original_count:
                    # Message was deleted
                    if not self.messages[user_uuid]:
                        # Remove empty message list
                        del self.messages[user_uuid]
                    
                    return self._save_messages_internal(self.messages)
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting message: {type(e).__name__}: {e}")
            return False
    
    def get_unread_message_count(self, user_uuid: str) -> int:
        """Get count of unread messages for a user
        
        Args:
            user_uuid: UUID of the user
            
        Returns:
            Number of unread messages
        """
        try:
            if user_uuid not in self.messages:
                return 0
            
            unread_count = sum(1 for msg in self.messages[user_uuid] if not msg.get('read', False))
            return unread_count
            
        except Exception as e:
            logger.error(f"Error getting unread message count: {type(e).__name__}: {e}")
            return 0
    
    def mark_all_messages_as_read(self, user_uuid: str) -> bool:
        """Mark all messages as read for a user
        
        Args:
            user_uuid: UUID of the user
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_uuid in self.messages:
                for message in self.messages[user_uuid]:
                    message['read'] = True
                return self._save_messages_internal(self.messages)
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking all messages as read: {type(e).__name__}: {e}")
            return False
    
    def get_messages_by_type(self, user_uuid: str, message_type: str, requesting_user_uuid: str, 
                           requesting_user_privileges: List[str]) -> List[Dict[str, Any]]:
        """Get messages of a specific type for a user
        
        Args:
            user_uuid: UUID of the user whose messages to retrieve
            message_type: Type of messages to retrieve
            requesting_user_uuid: UUID of the user making the request
            requesting_user_privileges: List of privileges for the requesting user
            
        Returns:
            List of messages of the specified type
        """
        try:
            # Check permissions
            if not self.access_control.can_access_user_messages(
                user_uuid, requesting_user_uuid, requesting_user_privileges
            ):
                return []
            
            if user_uuid not in self.messages:
                return []
            
            filtered_messages = [
                msg for msg in self.messages[user_uuid] 
                if msg.get('message_type') == message_type
            ]
            
            return filtered_messages
            
        except Exception as e:
            logger.error(f"Error getting messages by type: {type(e).__name__}: {e}")
            return []
    
    def send_message_to_company_users(self, company_id: str, message: str, author_uuid: str, 
                                    message_type: str = "general", exclude_user_uuids: List[str] = None) -> bool:
        """Send a message to all users in a company
        
        Args:
            company_id: ID of the company
            message: Message content
            author_uuid: UUID of the message author
            message_type: Type of message
            exclude_user_uuids: Optional list of user UUIDs to exclude
            
        Returns:
            True if at least one message was sent successfully
        """
        try:
            if exclude_user_uuids is None:
                exclude_user_uuids = []
            
            # Get all users in the company
            company_users = []
            for email, user_data in self.user_storage.users.items():
                if (isinstance(user_data, dict) and 
                    user_data.get('company_id') == company_id and
                    user_data.get('uuid') not in exclude_user_uuids):
                    company_users.append(user_data.get('uuid'))
            
            success_count = 0
            for user_uuid in company_users:
                if self._add_message_internal(user_uuid, message, author_uuid, message_type):
                    success_count += 1
            
            logger.info(f"Sent message to {success_count}/{len(company_users)} users in company {company_id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending message to company users: {type(e).__name__}: {e}")
            return False
    
    # Disciplinary action methods (delegated to DisciplinaryActionManager)
    def send_warning_to_subordinates(self, sender_uuid: str, message: str, 
                                   target_user_uuids: List[str] = None) -> Dict[str, Any]:
        """Send warning messages to subordinates"""
        return self.disciplinary_manager.send_warning_to_subordinates(
            sender_uuid, message, target_user_uuids
        )
    
    def send_disciplinary_action(self, sender_uuid: str, target_user_uuid: str, 
                               action_type: str, message: str, severity: str = "medium") -> Dict[str, Any]:
        """Send disciplinary action messages"""
        return self.disciplinary_manager.send_disciplinary_action(
            sender_uuid, target_user_uuid, action_type, message, severity
        )
    
    # Statistics methods (delegated to MessageStatistics)
    def get_message_statistics(self, user_uuid: str = None, company_id: str = None) -> Dict[str, Any]:
        """Get message statistics"""
        return self.statistics.get_message_statistics(self.messages, user_uuid, company_id)
    
    def get_user_statistics(self, user_uuid: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific user"""
        return self.statistics.get_user_statistics(self.messages, user_uuid)
    
    def get_company_statistics(self, company_id: str) -> Dict[str, Any]:
        """Get statistics for all users in a company"""
        return self.statistics.get_company_statistics(self.messages, company_id)
    
    def get_system_wide_statistics(self) -> Dict[str, Any]:
        """Get system-wide message statistics"""
        return self.statistics.get_system_wide_statistics(self.messages)
    
    # Cleanup methods (delegated to MessageCleanup)
    def cleanup_old_messages(self, days_old: int = 90, user_uuid: str = None) -> int:
        """Clean up old messages"""
        return self.cleanup.cleanup_old_messages(self.messages, days_old, user_uuid)
    
    def cleanup_user_messages(self, user_uuid: str) -> bool:
        """Clean up messages for a deleted user"""
        return self.cleanup.cleanup_user_messages(self.messages, user_uuid)
    
    def cleanup_messages_by_type(self, message_type: str, user_uuid: str = None) -> int:
        """Clean up messages of a specific type"""
        return self.cleanup.cleanup_messages_by_type(self.messages, message_type, user_uuid)
    
    def cleanup_read_messages(self, user_uuid: str = None, older_than_days: int = 30) -> int:
        """Clean up read messages older than specified days"""
        return self.cleanup.cleanup_read_messages(self.messages, user_uuid, older_than_days)
    
    def optimize_message_storage(self) -> Dict[str, Any]:
        """Optimize message storage"""
        return self.cleanup.optimize_message_storage(self.messages)
    
    def archive_old_messages(self, days_old: int = 365, archive_path: str = None) -> Dict[str, Any]:
        """Archive old messages"""
        return self.cleanup.archive_old_messages(self.messages, days_old, archive_path)
    
    # Internal helper methods
    def _add_message_internal(self, user_uuid: str, message: str, author_uuid: str, 
                             message_type: str = "general") -> bool:
        """Internal method to add a message"""
        try:
            if user_uuid not in self.messages:
                self.messages[user_uuid] = []
            
            message_entry = {
                'id': f"msg_{int(time.time())}_{len(self.messages[user_uuid])}",
                'content': message,
                'author_uuid': author_uuid,
                'message_type': message_type,
                'timestamp': time.time(),
                'created_at': datetime.now().isoformat(),
                'read': False
            }
            
            self.messages[user_uuid].append(message_entry)
            
            return self._save_messages_internal(self.messages)
            
        except Exception as e:
            logger.error(f"Error adding user message: {type(e).__name__}: {e}")
            return False
    
    def _save_messages_internal(self, messages: Dict[str, Any]) -> bool:
        """Internal method to save messages"""
        return self.storage.save_messages(messages)
"""
Message Access Control Module

Handles permissions and access control for messaging operations.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class MessageAccessControl:
    """Handles message access control and permissions"""
    
    @staticmethod
    def can_access_user_messages(user_uuid: str, requesting_user_uuid: str, 
                                requesting_user_privileges: List[str]) -> bool:
        """Check if requesting user can access another user's messages"""
        # Users can see their own messages
        if user_uuid == requesting_user_uuid:
            return True
        
        # Admins/owners can see all messages
        if any(priv in ['owner', 'admin'] for priv in requesting_user_privileges):
            return True
        
        logger.warning(f"User {requesting_user_uuid} cannot access messages for {user_uuid}")
        return False
    
    @staticmethod
    def can_delete_message(user_uuid: str, requesting_user_uuid: str,
                          requesting_user_privileges: List[str]) -> bool:
        """Check if requesting user can delete messages for another user"""
        # Users can delete their own messages
        if user_uuid == requesting_user_uuid:
            return True
        
        # Admins/owners can delete any messages
        if any(priv in ['owner', 'admin'] for priv in requesting_user_privileges):
            return True
        
        logger.warning(f"User {requesting_user_uuid} cannot delete messages for {user_uuid}")
        return False
    
    @staticmethod
    def can_send_warnings(sender_privileges: List[str]) -> bool:
        """Check if user can send warning messages"""
        return any(priv in ['owner', 'admin', 'manager'] for priv in sender_privileges)
    
    @staticmethod
    def can_send_disciplinary_actions(sender_privileges: List[str]) -> bool:
        """Check if user can send disciplinary actions"""
        return any(priv in ['owner', 'admin'] for priv in sender_privileges)
    
    @staticmethod
    def can_discipline_user(sender_privileges: List[str], target_privileges: List[str]) -> bool:
        """Check if sender can discipline target user"""
        # Owners cannot be disciplined by admins
        if 'owner' in target_privileges and 'owner' not in sender_privileges:
            return False
        return True
    
    @staticmethod
    def get_privilege_hierarchy() -> List[str]:
        """Get privilege hierarchy (higher index = lower privilege)"""
        return [
            "owner",        # 0 - highest
            "admin",        # 1
            "manager",      # 2
            "dispatcher",   # 3
            "engineer",     # 4
            "fuel_manager", # 5
            "fleet_officer", # 6
            "analyst",      # 7
            "viewer"        # 8 - lowest
        ]
    
    @staticmethod
    def get_privilege_level(privileges: List[str]) -> int:
        """Get the highest privilege level for a user (lower number = higher privilege)"""
        hierarchy = MessageAccessControl.get_privilege_hierarchy()
        
        for i, priv in enumerate(hierarchy):
            if priv in privileges:
                return i
        
        return 999  # Default to lowest if not found
    
    @staticmethod
    def is_subordinate(manager_privileges: List[str], user_privileges: List[str]) -> bool:
        """Check if user is subordinate to manager"""
        manager_level = MessageAccessControl.get_privilege_level(manager_privileges)
        user_level = MessageAccessControl.get_privilege_level(user_privileges)
        
        # User is subordinate if they have higher index (lower privilege)
        return user_level > manager_level
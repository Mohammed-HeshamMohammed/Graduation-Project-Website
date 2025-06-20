import logging
from typing import List, Dict, Any, Optional
from app.services.storage import UserStorage

# Configure logging
logger = logging.getLogger(__name__)


class PrivilegeManager:
    """Handles user privilege management and validation"""
    
    # Privilege hierarchy - lower index means higher privilege
    HIERARCHY_ORDER = [
        "owner", "admin", "manager", "dispatcher", 
        "engineer", "fuel_manager", "fleet_officer", "analyst", "viewer"
    ]
    
    def __init__(self, storage: UserStorage):
        """
        Initialize privilege manager
        
        Args:
            storage: UserStorage instance for accessing privilege hierarchy
        """
        self.storage = storage
    
    def has_privilege(self, user_privileges: List[str], required_privilege: str) -> bool:
        """
        Check if user has a specific privilege or higher
        
        Args:
            user_privileges: List of user's privileges
            required_privilege: Required privilege to check
            
        Returns:
            bool: True if user has the required privilege or higher
        """
        try:
            if not user_privileges or not isinstance(user_privileges, list):
                return False
            
            # Check direct privilege match
            if required_privilege in user_privileges:
                return True
            
            # Check hierarchy for dashboard privileges
            user_level = self._get_highest_privilege_level(user_privileges)
            required_level = self._get_privilege_level(required_privilege)
            
            # If user has higher privilege level (lower index), they have access
            return user_level != -1 and required_level != -1 and user_level <= required_level
            
        except Exception as e:
            logger.error(f"Error checking privilege: {type(e).__name__}: {e}")
            return False
    
    def can_access_feature(self, user_privileges: List[str], feature: str) -> bool:
        """
        Check if user can access a specific feature based on privilege hierarchy
        
        Args:
            user_privileges: List of user's privileges
            feature: Feature name to check access for
            
        Returns:
            bool: True if user can access the feature
        """
        try:
            if not user_privileges or not isinstance(user_privileges, list):
                return False
            
            # Get feature privileges from storage if available
            feature_privileges = getattr(self.storage, 'PRIVILEGE_HIERARCHY', {}).get(feature, [])
            
            return any(priv in feature_privileges for priv in user_privileges)
            
        except Exception as e:
            logger.error(f"Error checking feature access: {type(e).__name__}: {e}")
            return False
    
    def get_user_privilege_level(self, user_privileges: List[str]) -> int:
        """
        Get the highest privilege level for a user
        
        Args:
            user_privileges: List of user's privileges
            
        Returns:
            int: Privilege level (lower number = higher privilege), -1 if no valid privileges
        """
        return self._get_highest_privilege_level(user_privileges)
    
    def is_higher_privilege(self, user_privileges: List[str], target_privileges: List[str]) -> bool:
        """
        Check if user has higher privilege than target user
        
        Args:
            user_privileges: User's privileges
            target_privileges: Target user's privileges
            
        Returns:
            bool: True if user has higher privilege
        """
        user_level = self._get_highest_privilege_level(user_privileges)
        target_level = self._get_highest_privilege_level(target_privileges)
        
        # Lower index means higher privilege
        return user_level != -1 and target_level != -1 and user_level < target_level
    
    def can_manage_user(self, manager_privileges: List[str], target_privileges: List[str]) -> bool:
        """
        Check if a user can manage another user based on privilege hierarchy
        
        Args:
            manager_privileges: Manager's privileges
            target_privileges: Target user's privileges
            
        Returns:
            bool: True if manager can manage the target user
        """
        # Owner can manage anyone except other owners
        if "owner" in manager_privileges:
            return "owner" not in target_privileges or manager_privileges == target_privileges
        
        # Admin can manage anyone below admin level
        if "admin" in manager_privileges:
            return not self._has_privilege_level(target_privileges, ["owner", "admin"])
        
        # Manager can manage anyone below manager level
        if "manager" in manager_privileges:
            return not self._has_privilege_level(target_privileges, ["owner", "admin", "manager"])
        
        # Other privileges cannot manage users
        return False
    
    def get_manageable_privileges(self, user_privileges: List[str]) -> List[str]:
        """
        Get list of privileges that a user can assign to others
        
        Args:
            user_privileges: User's privileges
            
        Returns:
            List[str]: List of privileges that can be assigned
        """
        if "owner" in user_privileges:
            # Owners can assign any privilege except owner
            return [p for p in self.HIERARCHY_ORDER if p != "owner"]
        
        if "admin" in user_privileges:
            # Admins can assign privileges below admin level
            return [p for p in self.HIERARCHY_ORDER if p not in ["owner", "admin"]]
        
        if "manager" in user_privileges:
            # Managers can assign privileges below manager level
            return [p for p in self.HIERARCHY_ORDER if p not in ["owner", "admin", "manager"]]
        
        # Other privileges cannot assign privileges
        return []
    
    def _get_highest_privilege_level(self, privileges: List[str]) -> int:
        """Get the highest privilege level from a list of privileges"""
        if not privileges or not isinstance(privileges, list):
            return -1
        
        for i, priv in enumerate(self.HIERARCHY_ORDER):
            if priv in privileges:
                return i
        
        return -1
    
    def _get_privilege_level(self, privilege: str) -> int:
        """Get the level of a specific privilege"""
        try:
            return self.HIERARCHY_ORDER.index(privilege)
        except ValueError:
            return -1
    
    def _has_privilege_level(self, privileges: List[str], check_privileges: List[str]) -> bool:
        """Check if user has any of the specified privilege levels"""
        if not privileges or not isinstance(privileges, list):
            return False
        
        return any(priv in privileges for priv in check_privileges)
    
    def get_privilege_hierarchy(self) -> List[str]:
        """
        Get the complete privilege hierarchy
        
        Returns:
            List[str]: Ordered list of privileges from highest to lowest
        """
        return self.HIERARCHY_ORDER.copy()
    
    def get_privilege_description(self, privilege: str) -> str:
        """
        Get a human-readable description of a privilege
        
        Args:
            privilege: Privilege name
            
        Returns:
            str: Description of the privilege
        """
        descriptions = {
            "owner": "Full system access and ownership",
            "admin": "Administrative access to all features",
            "manager": "Management access to team and operations",
            "dispatcher": "Dispatch and coordination operations",
            "engineer": "Technical and engineering operations",
            "fuel_manager": "Fuel management and monitoring",
            "fleet_officer": "Fleet operations and management",
            "analyst": "Data analysis and reporting",
            "viewer": "Read-only access to information"
        }
        
        return descriptions.get(privilege, f"Unknown privilege: {privilege}")
    
    def validate_privilege_assignment(self, assigner_privileges: List[str], 
                                    target_privileges: List[str], 
                                    new_privileges: List[str]) -> tuple[bool, str]:
        """
        Validate if a privilege assignment is allowed
        
        Args:
            assigner_privileges: Privileges of the user making the assignment
            target_privileges: Current privileges of the target user
            new_privileges: New privileges to assign
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check if assigner can manage the target user
            if not self.can_manage_user(assigner_privileges, target_privileges):
                return False, "Insufficient privileges to manage this user"
            
            # Check if assigner can assign the new privileges
            manageable_privileges = self.get_manageable_privileges(assigner_privileges)
            
            for priv in new_privileges:
                if priv not in manageable_privileges and priv not in target_privileges:
                    return False, f"Cannot assign privilege: {priv}"
            
            return True, "Privilege assignment is valid"
            
        except Exception as e:
            logger.error(f"Error validating privilege assignment: {type(e).__name__}: {e}")
            return False, f"Validation error: {str(e)}"
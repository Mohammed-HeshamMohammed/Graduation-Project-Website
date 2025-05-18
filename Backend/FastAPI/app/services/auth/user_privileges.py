# app/services/auth/user_privileges.py
import logging
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

class UserPrivilege:
    # Core privileges (existing)
    OWNER = "owner"           # Can do everything, cannot be removed
    ADMIN = "admin"           # Can add/remove users and assign privileges
    ADD_MEMBERS = "add"       # Can only add new members
    REMOVE_MEMBERS = "remove" # Can only remove members
    MEMBER = "member"         # Basic member with no special privileges
    
    # Dashboard-specific roles (new)
    MANAGER = "manager"       # Can control everything in the dashboard
    DISPATCHER = "dispatcher" # Can only control trips in the dashboard
    VIEWER = "viewer"         # Can only view the dashboard without making changes
    
    @staticmethod
    def get_all_privileges() -> Set[str]:
        """Return all available privileges"""
        return {
            UserPrivilege.OWNER, 
            UserPrivilege.ADMIN,
            UserPrivilege.ADD_MEMBERS, 
            UserPrivilege.REMOVE_MEMBERS,
            UserPrivilege.MEMBER,
            UserPrivilege.MANAGER,
            UserPrivilege.DISPATCHER,
            UserPrivilege.VIEWER
        }
    
    @staticmethod
    def is_valid_privilege(privilege: str) -> bool:
        """Check if a privilege is valid"""
        return privilege in UserPrivilege.get_all_privileges()
    
    @staticmethod
    def get_dashboard_privileges() -> Set[str]:
        """Return dashboard-specific privileges"""
        return {
            UserPrivilege.MANAGER,
            UserPrivilege.DISPATCHER,
            UserPrivilege.VIEWER
        }

def get_user_privileges(privileges: List[str]) -> Set[str]:
    """
    Get a set of valid privileges from a list
    Args: privileges: List of privilege strings
    Returns: Set of valid privileges
    """
    if not privileges:
        return {UserPrivilege.MEMBER}
    
    # Filter out invalid privileges
    valid_privileges = {priv for priv in privileges 
                        if UserPrivilege.is_valid_privilege(priv)}
    
    # If no valid privileges found, return MEMBER as default
    if not valid_privileges:
        return {UserPrivilege.MEMBER}
    
    return valid_privileges

# Core permission functions (existing)
def can_add_members(privileges: List[str]) -> bool:
    """Check if user can add members based on privileges"""
    user_privs = get_user_privileges(privileges)
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN, UserPrivilege.ADD_MEMBERS])

def can_remove_members(privileges: List[str]) -> bool:
    """Check if user can remove members based on privileges"""
    user_privs = get_user_privileges(privileges)
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN, UserPrivilege.REMOVE_MEMBERS])

def can_manage_privileges(privileges: List[str]) -> bool:
    """Check if user can manage privileges of other users"""
    user_privs = get_user_privileges(privileges)
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN])

def is_owner(privileges: List[str]) -> bool:
    """Check if user is the owner"""
    user_privs = get_user_privileges(privileges)
    return UserPrivilege.OWNER in user_privs

# Dashboard permission functions (new)
def can_access_dashboard(privileges: List[str]) -> bool:
    """Check if user can access the dashboard at all"""
    user_privs = get_user_privileges(privileges)
    # Owner, Admin, and all dashboard roles can access
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN, 
               UserPrivilege.MANAGER, UserPrivilege.DISPATCHER, UserPrivilege.VIEWER])

def can_manage_dashboard(privileges: List[str]) -> bool:
    """Check if user can manage everything in the dashboard"""
    user_privs = get_user_privileges(privileges)
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN, UserPrivilege.MANAGER])

def can_manage_trips(privileges: List[str]) -> bool:
    """Check if user can manage trips in the dashboard"""
    user_privs = get_user_privileges(privileges)
    return any(priv in user_privs for priv in 
              [UserPrivilege.OWNER, UserPrivilege.ADMIN, 
               UserPrivilege.MANAGER, UserPrivilege.DISPATCHER])

def can_view_only(privileges: List[str]) -> bool:
    """Check if user is restricted to view-only access"""
    user_privs = get_user_privileges(privileges)
    # If they're ONLY a viewer (and not any higher permission)
    higher_permissions = {UserPrivilege.OWNER, UserPrivilege.ADMIN, 
                         UserPrivilege.MANAGER, UserPrivilege.DISPATCHER}
    return UserPrivilege.VIEWER in user_privs and not any(priv in user_privs for priv in higher_permissions)

def get_dashboard_role(privileges: List[str]) -> Optional[str]:
    """
    Get the highest dashboard role for a user
    Args: privileges: List of privilege strings
    Returns: The highest dashboard role or None if no dashboard roles
    """
    user_privs = get_user_privileges(privileges)
    
    # Check roles in descending order of permissions
    if UserPrivilege.OWNER in user_privs or UserPrivilege.ADMIN in user_privs:
        return UserPrivilege.MANAGER  # Owners and admins have full manager rights
    elif UserPrivilege.MANAGER in user_privs:
        return UserPrivilege.MANAGER
    elif UserPrivilege.DISPATCHER in user_privs:
        return UserPrivilege.DISPATCHER
    elif UserPrivilege.VIEWER in user_privs:
        return UserPrivilege.VIEWER
    
    return None  # No dashboard role
"""
Access control mixin providing privilege-based access control functionality.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AccessControlMixin:
    """Mixin class providing access control functionality."""
    
    def __init__(self):
        """Initialize access control with privilege hierarchy."""
        # Privilege hierarchy for access control
        self.PRIVILEGE_HIERARCHY = {
            "dashboard_access": [
                "owner", "admin", "manager", "dispatcher",
                "engineer", "fuel_manager", "fleet_officer", "analyst", "viewer"
            ],
            "trip_management": [
                "owner", "admin", "manager", "dispatcher"
            ],
            "maintenance_access": [
                "owner", "admin", "manager", "engineer"
            ],
            "fuel_access": [
                "owner", "admin", "manager", "fuel_manager"  
            ],
            "fleet_management": [
                "owner", "admin", "manager", "fleet_officer"
            ],
            "analytics_access": [
                "owner", "admin", "manager", "analyst"
            ],
            "view_only": [
                "viewer", "analyst"
            ],
            "user_management": [
                "owner", "admin", "add", "remove"
            ]
        }
    
    def has_privilege(self, user_privileges: List[str], required_privilege: str) -> bool:
        """
        Check if user has required privilege.
        
        Args:
            user_privileges: List of user's privileges
            required_privilege: Required privilege to check
            
        Returns:
            True if user has the privilege, False otherwise
        """
        if not user_privileges or not isinstance(user_privileges, list):
            return False
        
        allowed_privileges = self.PRIVILEGE_HIERARCHY.get(required_privilege, [])
        return any(priv in allowed_privileges for priv in user_privileges)
    
    def can_access_user_data(self, requesting_user: Dict[str, Any], target_user: Dict[str, Any]) -> bool:
        """
        Check if requesting user can access target user's data.
        
        Args:
            requesting_user: User making the request
            target_user: User whose data is being accessed
            
        Returns:
            True if access is allowed, False otherwise
        """
        if not requesting_user or not target_user:
            return False
        
        # Users can always access their own data
        if requesting_user.get('email') == target_user.get('email'):
            return True
        
        # Check if same company
        requesting_company = requesting_user.get('company_id')
        target_company = target_user.get('company_id')
        
        if not requesting_company or not target_company:
            return False
        
        if requesting_company != target_company:
            return False
        
        # Users in same company can access each other's basic data
        return True
    
    def get_filtered_user_data(self, user_data: Dict[str, Any], requesting_user: Dict[str, Any], 
                              is_own_data: bool = False) -> Dict[str, Any]:
        """
        Filter user data based on access level.
        
        Args:
            user_data: User data to filter
            requesting_user: User making the request
            is_own_data: Whether this is the user's own data
            
        Returns:
            Filtered user data
        """
        if not user_data or not isinstance(user_data, dict):
            return {}
        
        # Create a copy to avoid modifying original
        filtered_data = user_data.copy()
        
        # Always remove sensitive fields
        for field in getattr(self, 'SENSITIVE_FIELDS', set()):
            filtered_data.pop(field, None)
        
        if is_own_data:
            # Users get their full data (minus sensitive fields)
            return filtered_data
        
        # For colleague data, return basic information
        colleague_data = {
            'uuid': filtered_data.get('uuid'),
            'email': filtered_data.get('email'),
            'full_name': filtered_data.get('full_name'),
            'company_id': filtered_data.get('company_id'),
            'verified': filtered_data.get('verified'),
            'is_logged_in': filtered_data.get('is_logged_in'),
            'privileges': filtered_data.get('privileges', []),
            'is_owner': filtered_data.get('is_owner'),
            'added_at': filtered_data.get('added_at')
        }
        
        # Additional data based on requesting user's privileges
        if requesting_user and isinstance(requesting_user, dict):
            requesting_privileges = requesting_user.get('privileges', [])
            
            # Owners and admins can see additional info
            if any(priv in ['owner', 'admin'] for priv in requesting_privileges):
                colleague_data.update({
                    'added_by': filtered_data.get('added_by'),
                    'added_by_email': filtered_data.get('added_by_email')
                })
        
        return colleague_data
    
    def validate_company_access(self, requesting_user: Dict[str, Any], company_id: str) -> bool:
        """
        Validate if user can access company data.
        
        Args:
            requesting_user: User making the request
            company_id: Company ID to check access for
            
        Returns:
            True if access is allowed, False otherwise
        """
        if not requesting_user or not isinstance(requesting_user, dict):
            logger.warning("Invalid requesting user for company access validation")
            return False
        
        if not company_id:
            logger.warning("Invalid company_id for access validation")
            return False
        
        user_company = requesting_user.get('company_id')
        if user_company != company_id:
            logger.warning(f"User {requesting_user.get('email')} cannot access company {company_id}")
            return False
        
        return True
    
    def filter_company_users(self, users: List[Dict[str, Any]], requesting_user: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter company users based on requesting user's access level.
        
        Args:
            users: List of user data dictionaries
            requesting_user: User making the request
            
        Returns:
            List of filtered user data
        """
        if not users or not requesting_user:
            return []
        
        filtered_users = []
        requesting_email = requesting_user.get('email')
        
        for user_data in users:
            if not isinstance(user_data, dict):
                continue
            
            is_own_data = (user_data.get('email') == requesting_email)
            filtered_user = self.get_filtered_user_data(user_data, requesting_user, is_own_data)
            
            if filtered_user:
                filtered_users.append(filtered_user)
        
        return filtered_users
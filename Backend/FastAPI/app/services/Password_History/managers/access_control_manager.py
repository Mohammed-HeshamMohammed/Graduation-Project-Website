# File: Password_History/managers/access_control_manager.py
"""Access control and validation manager"""

from typing import Dict, Any
from .base_manager import BaseManager
from ..exceptions.password_exceptions import ValidationException

class AccessControlManager(BaseManager):
    """Handles access control and user validation"""
    
    def __init__(self, user_storage, config: Dict[str, Any] = None):
        super().__init__(config)
        self.user_storage = user_storage
    
    def validate_user_access(self, user_uuid: str, company_uuid: str, 
                           requesting_user_uuid: str = None) -> Dict[str, Any]:
        """Validate user access and return user data"""
        # Validate access permissions
        if requesting_user_uuid and requesting_user_uuid != user_uuid:
            self._validate_admin_access(requesting_user_uuid, company_uuid, self.user_storage)
        
        # Get user data
        user_data = self.user_storage.get_user_by_uuid(user_uuid)
        if not user_data:
            raise ValidationException(f"User not found: {user_uuid}")
        
        user_email = user_data.get('email')
        if not user_email:
            raise ValidationException(f"User email not found: {user_uuid}")
        
        return user_data
    
    def validate_admin_operation(self, admin_uuid: str, company_uuid: str = None) -> Dict[str, Any]:
        """Validate admin operation and return admin data"""
        admin_user = self.user_storage.get_user_by_uuid(admin_uuid)
        if not admin_user:
            raise ValidationException(f"Admin user not found: {admin_uuid}")
        
        if not admin_user.get('is_admin', False):
            raise ValidationException("User does not have admin privileges")
        
        if company_uuid and admin_user.get('company_uuid') != company_uuid:
            raise ValidationException("Admin does not belong to target company")
        
        return admin_user
    
    def validate_bypass_permission(self, admin_uuid: str, company_uuid: str) -> bool:
        """Validate permission to bypass history checks"""
        admin_user = self.validate_admin_operation(admin_uuid, company_uuid)
        return admin_user.get('is_admin', False)

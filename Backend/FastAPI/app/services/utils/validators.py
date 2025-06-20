import logging
from typing import List, Dict, Any, Set

# Configure logging
logger = logging.getLogger(__name__)


class UserValidator:
    """Handles user data validation"""
    
    # Define valid privileges as a class constant
    VALID_PRIVILEGES: Set[str] = {
        'owner', 'admin', 'add', 'remove', 'manager', 'dispatcher',
        'engineer', 'fuel_manager', 'fleet_officer', 'analyst', 'viewer'
    }
    
    # Required fields for user data
    REQUIRED_FIELDS = ['uuid', 'email', 'password', 'full_name', 'company_id']
    
    # Boolean fields that should be validated as booleans
    BOOLEAN_FIELDS = ['verified', 'is_logged_in', 'is_owner']
    
    def __init__(self):
        """Initialize the validator"""
        pass
    
    def validate_user_data(self, user_data: dict) -> tuple[bool, str]:
        """
        Validate user data structure according to schema
        
        Args:
            user_data: Dictionary containing user data to validate
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        try:
            # Check if user_data is a dictionary
            if not isinstance(user_data, dict):
                return False, "User data must be a dictionary"
            
            # Check required fields
            validation_result = self._validate_required_fields(user_data)
            if not validation_result[0]:
                return validation_result
            
            # Validate field types and values
            validation_result = self._validate_field_types(user_data)
            if not validation_result[0]:
                return validation_result
            
            # Validate boolean fields
            validation_result = self._validate_boolean_fields(user_data)
            if not validation_result[0]:
                return validation_result
            
            # Validate privileges
            validation_result = self._validate_privileges(user_data)
            if not validation_result[0]:
                return validation_result
            
            return True, "Valid user data"
            
        except Exception as e:
            logger.error(f"Error validating user data: {type(e).__name__}: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _validate_required_fields(self, user_data: dict) -> tuple[bool, str]:
        """Validate that all required fields are present"""
        for field in self.REQUIRED_FIELDS:
            if field not in user_data:
                logger.error(f"Missing required field: {field}")
                return False, f"Missing required field: {field}"
        return True, ""
    
    def _validate_field_types(self, user_data: dict) -> tuple[bool, str]:
        """Validate field types and basic format requirements"""
        # Validate UUID
        if not isinstance(user_data.get('uuid'), str) or not user_data['uuid'].strip():
            return False, "Invalid UUID"
        
        # Validate email
        email = user_data.get('email')
        if not isinstance(email, str) or '@' not in email or not email.strip():
            return False, "Invalid email format"
        
        # Validate full name
        full_name = user_data.get('full_name')
        if not isinstance(full_name, str) or not full_name.strip():
            return False, "Invalid full name"
        
        # Validate company ID
        company_id = user_data.get('company_id')
        if not isinstance(company_id, str) or not company_id.strip():
            return False, "Invalid company ID"
        
        # Validate password (basic check - should be string and not empty)
        password = user_data.get('password')
        if not isinstance(password, str) or not password:
            return False, "Invalid password"
        
        return True, ""
    
    def _validate_boolean_fields(self, user_data: dict) -> tuple[bool, str]:
        """Validate boolean fields"""
        for field in self.BOOLEAN_FIELDS:
            if field in user_data and not isinstance(user_data[field], bool):
                return False, f"Field {field} must be boolean"
        return True, ""
    
    def _validate_privileges(self, user_data: dict) -> tuple[bool, str]:
        """Validate privileges field"""
        if 'privileges' not in user_data:
            return True, ""  # Privileges are optional
        
        privileges = user_data['privileges']
        if not isinstance(privileges, list):
            return False, "Privileges must be a list"
        
        for priv in privileges:
            if not isinstance(priv, str):
                return False, f"Privilege must be a string, got {type(priv)}"
            if priv not in self.VALID_PRIVILEGES:
                return False, f"Invalid privilege: {priv}"
        
        return True, ""
    
    def validate_email_format(self, email: str) -> bool:
        """
        Validate email format (basic validation)
        
        Args:
            email: Email string to validate
            
        Returns:
            bool: True if email format is valid
        """
        if not isinstance(email, str):
            return False
        
        email = email.strip()
        if not email:
            return False
        
        # Basic email validation
        if '@' not in email:
            return False
        
        local, domain = email.rsplit('@', 1)
        if not local or not domain:
            return False
        
        if '.' not in domain:
            return False
        
        return True
    
    def validate_uuid_format(self, uuid: str) -> bool:
        """
        Validate UUID format (basic validation)
        
        Args:
            uuid: UUID string to validate
            
        Returns:
            bool: True if UUID format appears valid
        """
        if not isinstance(uuid, str):
            return False
        
        uuid = uuid.strip()
        if not uuid:
            return False
        
        # Basic UUID validation - should be non-empty string
        # You might want to add more specific UUID format validation here
        return len(uuid) > 0
    
    def validate_company_id(self, company_id: str) -> bool:
        """
        Validate company ID format
        
        Args:
            company_id: Company ID string to validate
            
        Returns:
            bool: True if company ID is valid
        """
        if not isinstance(company_id, str):
            return False
        
        company_id = company_id.strip()
        return len(company_id) > 0
    
    def get_valid_privileges(self) -> Set[str]:
        """
        Get the set of valid privileges
        
        Returns:
            Set of valid privilege strings
        """
        return self.VALID_PRIVILEGES.copy()
    
    def is_valid_privilege(self, privilege: str) -> bool:
        """
        Check if a privilege is valid
        
        Args:
            privilege: Privilege string to check
            
        Returns:
            bool: True if privilege is valid
        """
        return isinstance(privilege, str) and privilege in self.VALID_PRIVILEGES
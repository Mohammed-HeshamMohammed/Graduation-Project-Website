# File: Password_History/utils/validators.py
"""Validation utilities for password history operations"""

import re
import logging
from typing import Any
from ..exceptions.password_exceptions import ValidationException

logger = logging.getLogger(__name__)

class PasswordHistoryValidator:
    """Validator for password history operations"""
    
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    def validate_uuid(self, uuid_value: str, field_name: str):
        """Validate UUID format"""
        if not uuid_value:
            raise ValidationException(f"{field_name} is required")
        
        if not isinstance(uuid_value, str):
            raise ValidationException(f"{field_name} must be a string")
        
        if not self.UUID_PATTERN.match(uuid_value):
            raise ValidationException(f"{field_name} is not a valid UUID format")
    
    def validate_password_hash(self, password_hash: str):
        """Validate password hash"""
        if not password_hash:
            raise ValidationException("password_hash is required")
        
        if not isinstance(password_hash, str):
            raise ValidationException("password_hash must be a string")
        
        if len(password_hash) < 32:  # Minimum hash length
            raise ValidationException("password_hash appears to be too short")
    
    def validate_max_history(self, max_history: int):
        """Validate max history count"""
        if not isinstance(max_history, int):
            raise ValidationException("max_history must be an integer")
        
        if max_history < 1:
            raise ValidationException("max_history must be at least 1")
        
        if max_history > 50:  # Reasonable upper limit
            raise ValidationException("max_history cannot exceed 50")
    
    def validate_company_access(self, user_company_uuid: str, target_company_uuid: str):
        """Validate that user has access to company resources"""
        if not user_company_uuid or not target_company_uuid:
            raise ValidationException("Company UUIDs are required for access validation")
        
        if user_company_uuid != target_company_uuid:
            raise ValidationException("Access denied: User does not belong to target company")

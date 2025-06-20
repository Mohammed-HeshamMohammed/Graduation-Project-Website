# File: Password_History/managers/password_operations_manager.py
"""Core password operations manager"""

from typing import Dict, Any, List
from .base_manager import BaseManager, with_retry
from ..exceptions.password_exceptions import (
    PasswordHistoryException, 
    PasswordReusedException, 
    ValidationException,
    StorageException
)

class PasswordOperationsManager(BaseManager):
    """Handles core password operations"""
    
    def __init__(self, history_service, access_control_manager, 
                 cache_manager, audit_service, config: Dict[str, Any] = None):
        super().__init__(config)
        self.history_service = history_service
        self.access_control = access_control_manager
        self.cache_manager = cache_manager
        self.audit_service = audit_service
    
    @with_retry(max_attempts=3)
    def add_password_to_history(self, user_uuid: str, company_uuid: str, 
                              password_hash: str, max_history: int = None, 
                              **kwargs) -> bool:
        """Add password to user's history"""
        max_history = max_history or self.config.get('default_max_history', 5)
        context = self._get_request_context(**kwargs)
        
        try:
            # Validate access
            user_data = self.access_control.validate_user_access(
                user_uuid, company_uuid, context.get('requesting_user_uuid')
            )
            
            result = self.history_service.add_password_to_history(
                user_uuid=user_uuid,
                company_uuid=company_uuid,
                password_hash=password_hash,
                email=user_data.get('email'),
                max_history=max_history,
                **context
            )
            
            # Clear relevant caches
            self.cache_manager.invalidate_user_cache(user_uuid)
            return result
        
        except StorageException as e:
            self.logger.error(f"Storage error adding password to history: {e}")
            raise PasswordHistoryException(f"Storage error: {e}")
        except Exception as e:
            self.logger.error(f"Error adding password to history: {e}")
            raise
    
    @with_retry(max_attempts=2)
    def check_password_in_history(self, user_uuid: str, password_hash: str, 
                                **kwargs) -> bool:
        """Check if password was used before with caching"""
        cache_key = f"password_check_{user_uuid}_{hash(password_hash)}"
        context = self._get_request_context(**kwargs)
        
        # Try cache first
        cached_result = self.cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        try:
            result = self.history_service.check_password_reuse(
                user_uuid=user_uuid,
                password_hash=password_hash,
                **context
            )
            
            # Cache the result
            self.cache_manager.set(cache_key, result, ttl=300)  # 5 minutes
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking password history: {e}")
            return False
    
    @with_retry(max_attempts=3)
    def update_user_password(self, user_uuid: str, company_uuid: str, 
                           new_password_hash: str, bypass_history_check: bool = False,
                           **kwargs) -> bool:
        """Update user password with validation"""
        context = self._get_request_context(**kwargs)
        requesting_user_uuid = context.get('requesting_user_uuid')
        
        try:
            # Validate access
            self.access_control.validate_user_access(
                user_uuid, company_uuid, requesting_user_uuid
            )
            
            # Handle bypass logic
            if bypass_history_check:
                self._handle_password_bypass(
                    user_uuid, company_uuid, new_password_hash, 
                    requesting_user_uuid, context
                )
                result = True
            else:
                result = self.history_service.update_user_password(
                    user_uuid=user_uuid,
                    company_uuid=company_uuid,
                    new_password_hash=new_password_hash,
                    **context
                )
            
            # Clear all caches for this user
            self.cache_manager.invalidate_user_cache(user_uuid)
            return result
            
        except PasswordReusedException as e:
            self.logger.warning(f"Password reuse attempted for user {user_uuid}")
            raise e
        except Exception as e:
            self.logger.error(f"Error updating user password: {e}")
            raise
    
    def _handle_password_bypass(self, user_uuid: str, company_uuid: str,
                              new_password_hash: str, requesting_user_uuid: str,
                              context: Dict[str, Any]):
        """Handle password history bypass logic"""
        if not self.access_control.validate_bypass_permission(requesting_user_uuid, company_uuid):
            raise ValidationException("Only admins can bypass history checks")
        
        # Log security event for bypass
        self.audit_service.log_security_event(
            event_type='password_history_bypass',
            user_uuid=user_uuid,
            company_uuid=company_uuid,
            severity='high',
            details={
                'requesting_admin': requesting_user_uuid,
                'ip_address': context.get('ip_address'),
                'user_agent': context.get('user_agent')
            }
        )
        
        # Direct password update and add to history
        user_data = self.access_control.user_storage.get_user_by_uuid(user_uuid)
        user_data['password'] = new_password_hash
        self.access_control.user_storage.update_user(user_data)
        
        self.history_service.add_password_to_history(
            user_uuid=user_uuid,
            company_uuid=company_uuid,
            password_hash=new_password_hash,
            **context
        )

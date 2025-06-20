# File: Password_History/managers/company_operations_manager.py
"""Company-level operations manager"""

from typing import Dict, Any, List
from .base_manager import BaseManager
from ..models.password_history import PasswordHistoryEntry

class CompanyOperationsManager(BaseManager):
    """Handles company-level operations"""
    
    def __init__(self, history_service, access_control_manager, 
                 cache_manager, audit_service, config: Dict[str, Any] = None):
        super().__init__(config)
        self.history_service = history_service
        self.access_control = access_control_manager
        self.cache_manager = cache_manager
        self.audit_service = audit_service
    
    def handle_user_company_transfer(self, user_uuid: str, old_company_uuid: str,
                                   new_company_uuid: str, requesting_admin_uuid: str,
                                   preserve_history: bool = True, **kwargs) -> bool:
        """Handle user transfer between companies"""
        context = self._get_request_context(**kwargs)
        context['requesting_user_uuid'] = requesting_admin_uuid
        
        try:
            # Validate admin access to both companies
            self.access_control.validate_admin_operation(requesting_admin_uuid, old_company_uuid)
            self.access_control.validate_admin_operation(requesting_admin_uuid, new_company_uuid)
            
            # Log the transfer
            self.audit_service.log_security_event(
                event_type='user_company_transfer',
                user_uuid=user_uuid,
                company_uuid=old_company_uuid,
                severity='medium',
                details={
                    'requesting_admin': requesting_admin_uuid,
                    'old_company': old_company_uuid,
                    'new_company': new_company_uuid,
                    'preserve_history': preserve_history,
                    'ip_address': context.get('ip_address'),
                    'user_agent': context.get('user_agent')
                }
            )
            
            if preserve_history:
                current_count = self.history_service.get_user_history_count(
                    user_uuid=user_uuid, **context
                )
                self.logger.info(f"Preserving {current_count} password history entries")
            else:
                self.history_service.clear_user_history(
                    user_uuid=user_uuid,
                    company_uuid=old_company_uuid,
                    **context
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling company transfer: {e}")
            return False
    
    def handle_company_merger(self, primary_company_uuid: str, merged_company_uuid: str,
                            requesting_admin_uuid: str, **kwargs) -> bool:
        """Handle company merger scenarios"""
        context = self._get_request_context(**kwargs)
        context['requesting_user_uuid'] = requesting_admin_uuid
        
        try:
            # Validate admin access to both companies
            self.access_control.validate_admin_operation(requesting_admin_uuid, primary_company_uuid)
            self.access_control.validate_admin_operation(requesting_admin_uuid, merged_company_uuid)
            
            # Log the merger
            self.audit_service.log_security_event(
                event_type='company_merger',
                company_uuid=primary_company_uuid,
                severity='high',
                details={
                    'requesting_admin': requesting_admin_uuid,
                    'primary_company': primary_company_uuid,
                    'merged_company': merged_company_uuid,
                    'ip_address': context.get('ip_address'),
                    'user_agent': context.get('user_agent')
                }
            )
            
            self.logger.info(f"Company merger initiated: {merged_company_uuid} -> {primary_company_uuid}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error handling company merger: {e}")
            return False
    
    def get_company_password_histories(self, company_uuid: str,
                                     requesting_user_uuid: str = None,
                                     use_cache: bool = True,
                                     **kwargs) -> Dict[str, List[PasswordHistoryEntry]]:
        """Get all password histories for users in a company"""
        cache_key = f"company_histories_{company_uuid}"
        context = self._get_request_context(**kwargs)
        context['requesting_user_uuid'] = requesting_user_uuid
        
        if use_cache:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        try:
            if requesting_user_uuid:
                user_data = self.access_control.user_storage.get_user_by_uuid(requesting_user_uuid)
                if not user_data or user_data.get('company_uuid') != company_uuid:
                    self.logger.warning(f"Access denied: User {requesting_user_uuid} cannot access company {company_uuid}")
                    return {}
            
            result = self.history_service.get_company_password_histories(
                company_uuid=company_uuid, **context
            )
            
            if use_cache:
                self.cache_manager.set(cache_key, result, ttl=1800)  # 30 minutes
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting company password histories: {e}")
            return {}
    
    def clear_user_history(self, user_uuid: str, company_uuid: str,
                          requesting_admin_uuid: str, **kwargs) -> bool:
        """Clear password history for a specific user (admin only)"""
        context = self._get_request_context(**kwargs)
        context['requesting_user_uuid'] = requesting_admin_uuid
        
        try:
            # Validate admin access
            self.access_control.validate_admin_operation(requesting_admin_uuid, company_uuid)
            
            return self.history_service.clear_user_history(
                user_uuid=user_uuid,
                company_uuid=company_uuid,
                **context
            )
            
        except Exception as e:
            self.logger.error(f"Error clearing user history: {e}")
            return False

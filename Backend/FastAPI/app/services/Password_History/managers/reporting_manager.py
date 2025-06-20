# File: Password_History/managers/reporting_manager.py
"""Reporting and analytics manager"""

import logging
from typing import Dict, Any, List

class ReportingManager:
    """Handles reporting, analytics and audit operations"""
    
    def __init__(self, audit_service, history_service, access_control_manager, config: Dict[str, Any] = None):
        self.audit_service = audit_service
        self.history_service = history_service
        self.access_control = access_control_manager
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_comprehensive_audit_trail(self, company_uuid: str = None, user_uuid: str = None,
                                    start_date: str = None, end_date: str = None,
                                    operation_type: str = None, requesting_user_uuid: str = None,
                                    limit: int = 1000) -> List[Dict]:
        """Get comprehensive audit trail with filtering"""
        try:
            if company_uuid and requesting_user_uuid:
                self.access_control.validate_admin_operation(requesting_user_uuid, company_uuid)
            
            return self.audit_service.get_audit_trail(
                company_uuid=company_uuid,
                user_uuid=user_uuid,
                start_date=start_date,
                end_date=end_date,
                operation_type=operation_type,
                limit=limit
            )
            
        except Exception as e:
            self.logger.error(f"Error getting audit trail: {e}")
            return []
    
    def get_security_summary(self, company_uuid: str = None, days: int = 30,
                           requesting_admin_uuid: str = None) -> Dict:
        """Get security event summary"""
        try:
            if company_uuid and requesting_admin_uuid:
                self.access_control.validate_admin_operation(requesting_admin_uuid, company_uuid)
            
            return self.audit_service.get_security_summary(
                company_uuid=company_uuid,
                days=days
            )
            
        except Exception as e:
            self.logger.error(f"Error getting security summary: {e}")
            return {}
    
    def get_statistics(self, company_uuid: str = None, requesting_user_uuid: str = None,
                      **kwargs) -> Dict:
        """Get password history statistics"""
        context = {
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'requesting_user_uuid': requesting_user_uuid
        }
        
        try:
            if company_uuid and requesting_user_uuid:
                self.access_control.validate_admin_operation(requesting_user_uuid, company_uuid)
            
            return self.history_service.get_statistics(
                company_uuid=company_uuid,
                **context
            )
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
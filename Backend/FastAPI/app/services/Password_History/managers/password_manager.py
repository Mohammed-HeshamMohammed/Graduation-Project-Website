# File: Password_History/managers/password_manager.py
"""Main password history manager - refactored facade"""

import logging
import threading
from typing import Dict, List, Optional, Any

from ..services.storage_service import UserStorageService, StorageException, FileManager
from ..services.history_service import PasswordHistoryService
from ..services.encryption_service import EncryptionService
from ..services.audit_service import AuditService
from ..utils.validators import PasswordHistoryValidator
from ..utils.backup_utils import BackupUtils
from ..utils.cache_manager import CacheManager
from ..utils.config_manager import ConfigManager
from ..models.password_history import PasswordHistoryEntry
from ..exceptions.password_exceptions import PasswordHistoryException

from .access_control_manager import AccessControlManager
from .password_operations_manager import PasswordOperationsManager
from .company_operations_manager import CompanyOperationsManager
from .reporting_manager import ReportingManager
from .system_manager import SystemManager

logger = logging.getLogger(__name__)

class PasswordHistoryManager:
    """Main manager class that orchestrates all password history operations"""
    
    _instance = None
    _lock = threading.RLock()
    
    def __init__(self, 
                 user_storage: UserStorageService = None,
                 data_dir: str = None,
                 config: Dict[str, Any] = None):
        """Initialize password history manager with component architecture"""
        
        # Initialize core services
        self.user_storage = user_storage or UserStorageService(data_dir)
        self.config = ConfigManager(config or {})
        self._operation_lock = threading.RLock()
        
        # Initialize supporting services
        self.encryption_service = EncryptionService()
        self.file_manager = FileManager(data_dir)
        self.validator = PasswordHistoryValidator()
        
        self.cache_manager = CacheManager(
            max_size=self.config.get('cache_max_size', 1000),
            ttl=self.config.get('cache_ttl', 3600)
        )
        
        # Initialize audit service
        if data_dir:
            self.audit_service = AuditService(data_dir)
        else:
            from app.config import settings
            self.audit_service = AuditService(settings.DATA_DIR)
        
        # Initialize history service
        self.history_service = PasswordHistoryService(
            user_storage=self.user_storage,
            file_manager=self.file_manager,
            validator=self.validator,
            audit_service=self.audit_service
        )
        
        # Initialize backup utils
        if data_dir:
            self.backup_utils = BackupUtils(data_dir)
        else:
            from app.config import settings
            self.backup_utils = BackupUtils(settings.DATA_DIR)
        
        # Initialize component managers
        self.access_control = AccessControlManager(self.user_storage, self.config.config)
        
        self.password_ops = PasswordOperationsManager(
            self.history_service, self.access_control, 
            self.cache_manager, self.audit_service, self.config.config
        )
        
        self.company_ops = CompanyOperationsManager(
            self.history_service, self.access_control,
            self.cache_manager, self.audit_service, self.config.config
        )
        
        self.reporting = ReportingManager(
            self.audit_service, self.history_service, 
            self.access_control, self.config.config
        )
        
        self.system = SystemManager(
            self.cache_manager, self.audit_service, self.file_manager,
            self.backup_utils, self.access_control, self.config.config
        )
        
        logger.info("Password history manager initialized with component architecture")
    
    @classmethod
    def get_instance(cls, user_storage: UserStorageService = None, 
                    data_dir: str = None, config: Dict[str, Any] = None):
        """Get singleton instance of password history manager"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(user_storage, data_dir, config)
        return cls._instance
    
    # Password Operations - Delegate to PasswordOperationsManager
    def add_password_to_history(self, user_uuid: str, company_uuid: str, 
                              password_hash: str, max_history: int = None, **kwargs) -> bool:
        """Add password to user's history"""
        return self.password_ops.add_password_to_history(
            user_uuid, company_uuid, password_hash, max_history, **kwargs
        )
    
    def check_password_in_history(self, user_uuid: str, password_hash: str, **kwargs) -> bool:
        """Check if password was used before"""
        return self.password_ops.check_password_in_history(user_uuid, password_hash, **kwargs)
    
    def update_user_password(self, user_uuid: str, company_uuid: str, 
                           new_password_hash: str, bypass_history_check: bool = False,
                           **kwargs) -> bool:
        """Update user password"""
        return self.password_ops.update_user_password(
            user_uuid, company_uuid, new_password_hash, bypass_history_check, **kwargs
        )
    
    # Company Operations - Delegate to CompanyOperationsManager
    def handle_user_company_transfer(self, user_uuid: str, old_company_uuid: str,
                                   new_company_uuid: str, requesting_admin_uuid: str,
                                   preserve_history: bool = True, **kwargs) -> bool:
        """Handle user transfer between companies"""
        return self.company_ops.handle_user_company_transfer(
            user_uuid, old_company_uuid, new_company_uuid, 
            requesting_admin_uuid, preserve_history, **kwargs
        )
    
    def handle_company_merger(self, primary_company_uuid: str, merged_company_uuid: str,
                            requesting_admin_uuid: str, **kwargs) -> bool:
        """Handle company merger scenarios"""
        return self.company_ops.handle_company_merger(
            primary_company_uuid, merged_company_uuid, requesting_admin_uuid, **kwargs
        )
    
    def get_company_password_histories(self, company_uuid: str, requesting_user_uuid: str = None,
                                     use_cache: bool = True, **kwargs) -> Dict[str, List[PasswordHistoryEntry]]:
        """Get all password histories for users in a company"""
        return self.company_ops.get_company_password_histories(
            company_uuid, requesting_user_uuid, use_cache, **kwargs
        )
    
    def clear_user_history(self, user_uuid: str, company_uuid: str,
                          requesting_admin_uuid: str, **kwargs) -> bool:
        """Clear password history for a specific user (admin only)"""
        return self.company_ops.clear_user_history(
            user_uuid, company_uuid, requesting_admin_uuid, **kwargs
        )
    
    # Reporting Operations - Delegate to ReportingManager
    def get_comprehensive_audit_trail(self, company_uuid: str = None, user_uuid: str = None,
                                    start_date: str = None, end_date: str = None,
                                    operation_type: str = None, requesting_user_uuid: str = None,
                                    limit: int = 1000) -> List[Dict]:
        """Get comprehensive audit trail with filtering"""
        return self.reporting.get_comprehensive_audit_trail(
            company_uuid, user_uuid, start_date, end_date,
            operation_type, requesting_user_uuid, limit
        )
    
    def get_security_summary(self, company_uuid: str = None, days: int = 30,
                           requesting_admin_uuid: str = None) -> Dict:
        """Get security event summary"""
        return self.reporting.get_security_summary(company_uuid, days, requesting_admin_uuid)
    
    def get_statistics(self, company_uuid: str = None, requesting_user_uuid: str = None,
                      **kwargs) -> Dict:
        """Get password history statistics"""
        return self.reporting.get_statistics(company_uuid, requesting_user_uuid, **kwargs)
    
    # System Operations - Delegate to SystemManager
    def get_performance_metrics(self, requesting_admin_uuid: str = None) -> Dict:
        """Get performance metrics for monitoring"""
        return self.system.get_performance_metrics(requesting_admin_uuid)
    
    def cleanup_and_optimize(self, requesting_admin_uuid: str = None, **kwargs) -> Dict:
        """Comprehensive cleanup and optimization"""
        return self.system.cleanup_and_optimize(requesting_admin_uuid, **kwargs)
    
    def create_backup(self, backup_path: str = None, requesting_admin_uuid: str = None,
                     **kwargs) -> bool:
        """Create a backup of password history data"""
        return self.system.create_backup(backup_path, requesting_admin_uuid, **kwargs)
    
    def shutdown(self):
        """Graceful shutdown with cleanup"""
        self.system.shutdown()
    
    # Direct History Service Operations
    def get_password_history_count(self, user_uuid: str, **kwargs) -> int:
        """Get password history count for a user"""
        context = self.password_ops._get_request_context(**kwargs)
        try:
            return self.history_service.get_user_history_count(user_uuid=user_uuid, **context)
        except Exception as e:
            logger.error(f"Error getting password history count: {e}")
            return 0
    
    def cleanup_orphaned_histories(self, requesting_admin_uuid: str = None, **kwargs) -> int:
        """Remove password histories for users that no longer exist"""
        context = self.password_ops._get_request_context(**kwargs)
        context['requesting_user_uuid'] = requesting_admin_uuid
        
        try:
            if requesting_admin_uuid:
                self.access_control.validate_admin_operation(requesting_admin_uuid)
            
            return self.history_service.cleanup_orphaned_histories(**context)
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned histories: {e}")
            return 0
    
    # Backward compatibility methods
    def check_password_reuse(self, user_uuid: str, password_hash: str, **kwargs) -> bool:
        """Alias for check_password_in_history"""
        return self.check_password_in_history(user_uuid, password_hash, **kwargs)
    
    def get_user_history_count(self, user_uuid: str, **kwargs) -> int:
        """Alias for get_password_history_count"""
        return self.get_password_history_count(user_uuid, **kwargs)
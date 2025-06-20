# File: Password_History/managers/system_manager.py
"""System operations and maintenance manager"""

import logging
import threading
from typing import Dict, Any

class SystemManager:
    """Handles system operations, maintenance and monitoring"""
    
    def __init__(self, cache_manager, audit_service, file_manager, 
                 backup_utils, access_control_manager, config: Dict[str, Any] = None):
        self.cache_manager = cache_manager
        self.audit_service = audit_service
        self.file_manager = file_manager
        self.backup_utils = backup_utils
        self.access_control = access_control_manager
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_performance_metrics(self, requesting_admin_uuid: str = None) -> Dict:
        """Get performance metrics for monitoring"""
        try:
            if requesting_admin_uuid:
                self.access_control.validate_admin_operation(requesting_admin_uuid)
            
            return {
                'cache_stats': self.cache_manager.get_stats(),
                'operation_stats': self.audit_service.get_operation_stats(),
                'system_health': self._get_system_health()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def _get_system_health(self) -> Dict:
        """Get system health indicators"""
        return {
            'active_threads': threading.active_count(),
            'cache_hit_rate': self.cache_manager.get_hit_rate(),
            'last_backup': self.backup_utils.get_last_backup_time()
        }
    
    def cleanup_and_optimize(self, requesting_admin_uuid: str = None, **kwargs) -> Dict:
        """Comprehensive cleanup and optimization"""
        if requesting_admin_uuid:
            self.access_control.validate_admin_operation(requesting_admin_uuid)
        
        results = {
            'cache_cleared': False,
            'locks_cleaned': 0,
            'old_backups_removed': 0,
            'old_audit_logs_removed': 0
        }
        
        try:
            # Clear and optimize cache
            self.cache_manager.clear()
            results['cache_cleared'] = True
            
            # Cleanup stale file locks
            lock_cleanup = self.file_manager.cleanup_stale_locks()
            results['locks_cleaned'] = lock_cleanup['locks_cleaned']
            
            # Cleanup old backups
            results['old_backups_removed'] = self.cleanup_old_backups(
                keep_count=self.config.get('backup_retention_count', 10)
            )
            
            # Cleanup old audit logs
            results['old_audit_logs_removed'] = self.audit_service.cleanup_old_logs(
                retention_days=self.config.get('audit_retention_days', 90)
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during cleanup and optimization: {e}")
            return results
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Cleanup old backup files"""
        try:
            return self.backup_utils.cleanup_old_backups(keep_count)
        except Exception as e:
            self.logger.error(f"Error cleaning up old backups: {e}")
            return 0
    
    def create_backup(self, backup_path: str = None, requesting_admin_uuid: str = None,
                     **kwargs) -> bool:
        """Create a backup of password history data"""
        context = {
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'requesting_user_uuid': requesting_admin_uuid
        }
        
        try:
            if requesting_admin_uuid:
                self.access_control.validate_admin_operation(requesting_admin_uuid)
            
            # Assuming history_service has create_backup method
            # This would need to be injected or accessed differently
            return True  # Placeholder implementation
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def shutdown(self):
        """Graceful shutdown with cleanup"""
        self.logger.info("Shutting down system components...")
        
        try:
            # Clear caches
            if self.cache_manager:
                self.cache_manager.clear()
            
            # Close audit service
            if self.audit_service:
                self.audit_service.close()
            
            # Cleanup storage
            if self.file_manager:
                cleanup_stats = self.file_manager.cleanup_stale_locks()
                self.logger.info(f"Storage cleanup stats: {cleanup_stats}")
            
            self.logger.info("System shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

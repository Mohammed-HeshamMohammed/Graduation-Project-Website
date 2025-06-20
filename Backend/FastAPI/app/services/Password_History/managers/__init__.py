# File: app/services/Password_History/managers/__init__.py
"""
Password History Managers

This module provides a comprehensive password history management system with the following architecture:

MAIN ENTRY POINT:
- PasswordHistoryManager: Main facade that coordinates all operations

SPECIALIZED MANAGERS:
- PasswordOperationsManager: Core password operations (add, check, update)
- CompanyOperationsManager: Company-level operations (transfers, mergers)
- AccessControlManager: User validation and access control
- ReportingManager: Analytics, audit trails, and reporting
- SystemManager: System maintenance, monitoring, and backups
- BaseManager: Common functionality and utilities

USAGE PATTERNS:

1. Initialize the main manager:
   ```python
   manager = PasswordHistoryManager.get_instance(
       user_storage=your_storage_service,
       data_dir="/path/to/data",
       config={"max_history": 10, "cache_ttl": 3600}
   )
   ```

2. Standard context parameters (optional for all methods):
   - ip_address: str - Client IP for audit logging
   - user_agent: str - Client user agent for audit logging
   - requesting_user_uuid: str - Who is making the request

=== PASSWORD OPERATIONS ===

manager.add_password_to_history(user_uuid, company_uuid, password_hash, max_history=None, **kwargs)
    PURPOSE: Add a new password to user's history
    EXPECTS:
        - user_uuid: str (required) - Target user's UUID
        - company_uuid: str (required) - User's company UUID
        - password_hash: str (required) - Hashed password to store
        - max_history: int (optional) - Max passwords to keep (default: 5)
        - **kwargs: Context parameters (ip_address, user_agent, requesting_user_uuid)
    RETURNS: bool - True if successful, False/Exception if failed
    EXCEPTIONS: PasswordHistoryException, StorageException, ValidationException

manager.check_password_in_history(user_uuid, password_hash, **kwargs)
    PURPOSE: Check if password was previously used by user
    EXPECTS:
        - user_uuid: str (required) - Target user's UUID
        - password_hash: str (required) - Hashed password to check
        - **kwargs: Context parameters
    RETURNS: bool - True if password was used before, False if not
    CACHING: Results cached for 5 minutes for performance

manager.update_user_password(user_uuid, company_uuid, new_password_hash, bypass_history_check=False, **kwargs)
    PURPOSE: Update user's password with history validation
    EXPECTS:
        - user_uuid: str (required) - Target user's UUID
        - company_uuid: str (required) - User's company UUID
        - new_password_hash: str (required) - New hashed password
        - bypass_history_check: bool (optional) - Skip history validation (admin only)
        - **kwargs: Context parameters
    RETURNS: bool - True if successful
    EXCEPTIONS: PasswordReusedException if password was used before
    SECURITY: bypass_history_check requires admin privileges and logs security event

=== COMPANY OPERATIONS ===

manager.handle_user_company_transfer(user_uuid, old_company_uuid, new_company_uuid, requesting_admin_uuid, preserve_history=True, **kwargs)
    PURPOSE: Transfer user between companies
    EXPECTS:
        - user_uuid: str (required) - User to transfer
        - old_company_uuid: str (required) - Source company
        - new_company_uuid: str (required) - Destination company
        - requesting_admin_uuid: str (required) - Admin performing transfer
        - preserve_history: bool (optional) - Keep password history (default: True)
        - **kwargs: Context parameters
    RETURNS: bool - True if successful
    SECURITY: Requires admin access to both companies, logs security event

manager.handle_company_merger(primary_company_uuid, merged_company_uuid, requesting_admin_uuid, **kwargs)
    PURPOSE: Handle company merger scenarios
    EXPECTS:
        - primary_company_uuid: str (required) - Company that will remain
        - merged_company_uuid: str (required) - Company being merged
        - requesting_admin_uuid: str (required) - Admin performing merger
        - **kwargs: Context parameters
    RETURNS: bool - True if successful
    SECURITY: Requires admin access to both companies, logs high-severity security event

manager.get_company_password_histories(company_uuid, requesting_user_uuid=None, use_cache=True, **kwargs)
    PURPOSE: Get all password histories for company users
    EXPECTS:
        - company_uuid: str (required) - Target company UUID
        - requesting_user_uuid: str (optional) - User making request
        - use_cache: bool (optional) - Use cached results (default: True)
        - **kwargs: Context parameters
    RETURNS: Dict[str, List[PasswordHistoryEntry]] - User UUID -> history entries
    CACHING: Results cached for 30 minutes
    ACCESS: User must belong to the company

manager.clear_user_history(user_uuid, company_uuid, requesting_admin_uuid, **kwargs)
    PURPOSE: Clear all password history for a user (admin only)
    EXPECTS:
        - user_uuid: str (required) - Target user's UUID
        - company_uuid: str (required) - User's company UUID
        - requesting_admin_uuid: str (required) - Admin performing action
        - **kwargs: Context parameters
    RETURNS: bool - True if successful
    SECURITY: Admin-only operation, logs security event

=== REPORTING & ANALYTICS ===

manager.get_comprehensive_audit_trail(company_uuid=None, user_uuid=None, start_date=None, end_date=None, operation_type=None, requesting_user_uuid=None, limit=1000)
    PURPOSE: Get filtered audit trail of system operations
    EXPECTS:
        - company_uuid: str (optional) - Filter by company
        - user_uuid: str (optional) - Filter by user
        - start_date: str (optional) - ISO format date string
        - end_date: str (optional) - ISO format date string
        - operation_type: str (optional) - Filter by operation type
        - requesting_user_uuid: str (optional) - User making request
        - limit: int (optional) - Max records to return (default: 1000)
    RETURNS: List[Dict] - Audit log entries with timestamps, operations, and details
    ACCESS: Admin access required for company-wide reports

manager.get_security_summary(company_uuid=None, days=30, requesting_admin_uuid=None)
    PURPOSE: Get summary of security events and trends
    EXPECTS:
        - company_uuid: str (optional) - Target company UUID
        - days: int (optional) - Days to look back (default: 30)
        - requesting_admin_uuid: str (optional) - Admin making request
    RETURNS: Dict - Security metrics, event counts, and trend analysis
    ACCESS: Admin access required

manager.get_statistics(company_uuid=None, requesting_user_uuid=None, **kwargs)
    PURPOSE: Get password history statistics and metrics
    EXPECTS:
        - company_uuid: str (optional) - Target company UUID
        - requesting_user_uuid: str (optional) - User making request
        - **kwargs: Context parameters
    RETURNS: Dict - Statistics like total users, avg history length, etc.
    ACCESS: Admin access required for company-wide stats

=== SYSTEM OPERATIONS ===

manager.get_performance_metrics(requesting_admin_uuid=None)
    PURPOSE: Get system performance and health metrics
    EXPECTS:
        - requesting_admin_uuid: str (optional) - Admin making request
    RETURNS: Dict - Cache stats, operation stats, system health indicators
    ACCESS: Admin access recommended

manager.cleanup_and_optimize(requesting_admin_uuid=None, **kwargs)
    PURPOSE: Perform system cleanup and optimization
    EXPECTS:
        - requesting_admin_uuid: str (optional) - Admin performing cleanup
        - **kwargs: Context parameters
    RETURNS: Dict - Cleanup results (cache_cleared, locks_cleaned, etc.)
    OPERATIONS: Clears cache, removes stale locks, cleans old backups and logs
    ACCESS: Admin access recommended

manager.create_backup(backup_path=None, requesting_admin_uuid=None, **kwargs)
    PURPOSE: Create backup of password history data
    EXPECTS:
        - backup_path: str (optional) - Custom backup location
        - requesting_admin_uuid: str (optional) - Admin creating backup
        - **kwargs: Context parameters
    RETURNS: bool - True if backup successful
    ACCESS: Admin access recommended

manager.shutdown()
    PURPOSE: Gracefully shutdown the manager and cleanup resources
    EXPECTS: No parameters
    RETURNS: None
    OPERATIONS: Clears caches, closes audit service, cleans up storage

=== UTILITY METHODS ===

manager.get_password_history_count(user_uuid, **kwargs)
    PURPOSE: Get count of password history entries for user
    EXPECTS:
        - user_uuid: str (required) - Target user's UUID
        - **kwargs: Context parameters
    RETURNS: int - Number of password history entries (0 if error)

manager.cleanup_orphaned_histories(requesting_admin_uuid=None, **kwargs)
    PURPOSE: Remove password histories for non-existent users
    EXPECTS:
        - requesting_admin_uuid: str (optional) - Admin performing cleanup
        - **kwargs: Context parameters
    RETURNS: int - Number of orphaned histories removed
    ACCESS: Admin access recommended

=== BACKWARD COMPATIBILITY ===

manager.check_password_reuse(user_uuid, password_hash, **kwargs)
    PURPOSE: Alias for check_password_in_history()
    
manager.get_user_history_count(user_uuid, **kwargs)
    PURPOSE: Alias for get_password_history_count()

=== EXCEPTION HANDLING ===

Common exceptions you should handle:
- PasswordHistoryException: General password history errors
- PasswordReusedException: Password was used before
- ValidationException: Invalid input or access denied
- StorageException: Database/storage errors
- ConcurrencyException: Multiple operations conflict (auto-retried)

=== CONFIGURATION OPTIONS ===

When initializing, you can provide a config dict with:
- default_max_history: int (default: 5) - Default password history length
- cache_max_size: int (default: 1000) - Maximum cache entries
- cache_ttl: int (default: 3600) - Cache time-to-live in seconds
- backup_retention_count: int (default: 10) - Number of backups to keep
- audit_retention_days: int (default: 90) - Days to keep audit logs

=== THREAD SAFETY ===

All operations are thread-safe with:
- RLock protection for critical sections
- Automatic retry on concurrency conflicts
- Singleton pattern for main manager instance

=== LOGGING ===

All operations are logged with appropriate levels:
- INFO: Normal operations
- WARNING: Retry attempts, access issues
- ERROR: Operation failures
- Security events logged to audit service
"""

from .password_manager import PasswordHistoryManager

__all__ = ["PasswordHistoryManager"]
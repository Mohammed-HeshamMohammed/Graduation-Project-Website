# File: app/services/Password_History/services/__init__.py
"""Password History Services Initialization Module

This module exposes the key services used in the password history system:
1. EncryptionService – Handles secure encryption and decryption.
2. StorageService – Manages how and where encrypted password data is stored.
3. PasswordHistoryService – Main logic handler for all password history operations.
4. AuditService – Comprehensive logging and compliance tracking.

SYSTEM ARCHITECTURE:
===================
    Application Layer
         |
    PasswordHistoryService  <-- Main business logic coordinator
         |
    +------+------+------+
    |      |      |      |
    v      v      v      v
Storage Encrypt Audit UserStorage
Service Service Service Service
    |
    v
UserStorageService (from storage_service package)
    |
    v
Encrypted Files (.enc format)

DATA FLOW EXAMPLE:
=================
1. User requests password change
2. PasswordHistoryService validates request
3. Checks for password reuse via StorageService
4. EncryptionService encrypts new password data
5. StorageService saves to UserStorageService
6. AuditService logs the entire operation
7. Response returned to application
"""

# Imports the main encryption utility class
from .encryption_service import EncryptionService

# Imports the storage layer service (file-based, user-based, or hybrid)
from .storage_service import StorageService

# Imports the main business logic for password history
from .history_service import PasswordHistoryService

# Imports the audit and compliance logging service
from .audit_service import AuditService

# Explicitly declares what will be available when this package is imported
__all__ = [
    "EncryptionService",     # Use for encrypting/decrypting password history data
    "StorageService",        # Use for storing/loading password history models securely
    "PasswordHistoryService", # Use for checking reuse, updating password, etc.
    "AuditService"           # Use for audit logging and compliance tracking
]

# ============================================================================
# COMPREHENSIVE USAGE GUIDE
# ============================================================================

"""
QUICK START EXAMPLE:
===================

from Password_History.services import (
    PasswordHistoryService, 
    StorageService, 
    EncryptionService,
    AuditService
)

# Initialize services (typically done once at application startup)
audit_service = AuditService(data_dir="/app/data/audit")
storage_service = StorageService(data_dir="/app/data/passwords")
history_service = PasswordHistoryService(
    storage_service=storage_service,
    audit_service=audit_service
)

# Example: Update user password with full audit trail
success = history_service.update_user_password(
    user_uuid="user-123-456",
    company_uuid="company-789",
    new_password_hash="$2b$12$hashed_password_here",
    requesting_user_uuid="admin-user-id",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)

# Example: Check if password was used before
is_reused = history_service.check_password_reuse(
    user_uuid="user-123-456",
    password_hash="$2b$12$hashed_password_here"
)

DETAILED SERVICE DOCUMENTATION:
==============================

1. PASSWORDHISTORYSERVICE - Main Business Logic
===============================================

INITIALIZATION:
    service = PasswordHistoryService(
        user_storage=None,          # Optional: UserStorage instance
        storage_service=None,       # Optional: StorageService instance
        validator=None,             # Optional: PasswordHistoryValidator instance
        audit_service=None          # Optional: AuditService instance
    )

KEY METHODS:

    add_password_to_history(user_uuid, company_uuid, password_hash, max_history=5, **audit_params)
    ↳ INPUTS:
        - user_uuid: str (required) - User's unique identifier
        - company_uuid: str (required) - Company's unique identifier  
        - password_hash: str (required) - Hashed password (never plaintext!)
        - max_history: int (optional, default=5) - Maximum passwords to keep
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: bool - True if successfully added, False otherwise
    ↳ RAISES: ValidationException for invalid inputs

    check_password_reuse(user_uuid, password_hash, **audit_params)
    ↳ INPUTS:
        - user_uuid: str (required) - User's unique identifier
        - password_hash: str (required) - Hashed password to check
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address  
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: bool - True if password was used before, False otherwise
    ↳ SIDE EFFECTS: Logs security event if password reuse detected

    update_user_password(user_uuid, company_uuid, new_password_hash, **audit_params)
    ↳ INPUTS:
        - user_uuid: str (required) - User's unique identifier
        - company_uuid: str (required) - Company's unique identifier
        - new_password_hash: str (required) - New hashed password
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent  
    ↳ RETURNS: bool - True if successfully updated, False otherwise
    ↳ RAISES: PasswordReusedException if password was used before
    ↳ SIDE EFFECTS: Updates user storage, adds to history, logs audit events

    get_company_password_histories(company_uuid, **audit_params)
    ↳ INPUTS:
        - company_uuid: str (required) - Company's unique identifier
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: Dict[str, List[PasswordHistoryEntry]] - User UUID -> history entries
    ↳ USAGE: For admin dashboards, compliance reports

    get_user_history_count(user_uuid, **audit_params)
    ↳ INPUTS:
        - user_uuid: str (required) - User's unique identifier
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: int - Number of passwords in user's history
    ↳ USAGE: For UI display, validation checks

    clear_user_history(user_uuid, company_uuid, **audit_params)
    ↳ INPUTS:
        - user_uuid: str (required) - User's unique identifier
        - company_uuid: str (required) - Company's unique identifier
        - requesting_user_uuid: str (optional) - Who made the request (should be admin)
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: bool - True if successfully cleared, False otherwise
    ↳ SECURITY: Logs high-severity security event, validates company membership
    ↳ USAGE: Admin function for compliance or user issues

    cleanup_orphaned_histories(**audit_params)
    ↳ INPUTS:
        - requesting_user_uuid: str (optional) - Who initiated cleanup
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: int - Number of orphaned histories removed
    ↳ USAGE: Maintenance operation, typically scheduled

    get_statistics(company_uuid=None, **audit_params)
    ↳ INPUTS:
        - company_uuid: str (optional) - Filter for specific company
        - requesting_user_uuid: str (optional) - Who made the request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: Dict - Statistics about password histories
        Example return: {
            'total_users_with_history': 150,
            'total_passwords_stored': 750,
            'average_passwords_per_user': 5.0,
            'users_by_history_count': {1: 20, 2: 30, 3: 50, 4: 30, 5: 20}
        }
    ↳ USAGE: Dashboard metrics, capacity planning

    create_backup(backup_path=None, **audit_params)
    ↳ INPUTS:
        - backup_path: str (optional) - Custom backup file path
        - requesting_user_uuid: str (optional) - Who initiated backup
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
    ↳ RETURNS: bool - True if backup created successfully
    ↳ USAGE: Manual backups, disaster recovery preparation

2. STORAGESERVICE - Data Persistence Layer
==========================================

INITIALIZATION:
    service = StorageService(
        data_dir="/path/to/data",   # Optional: Custom data directory
        encryption_service=None     # Optional: Custom EncryptionService
    )

KEY METHODS:

    load_password_history()
    ↳ INPUTS: None
    ↳ RETURNS: PasswordHistoryModel - Complete password history model
    ↳ USAGE: Load all password histories into memory for processing

    save_password_history(model)
    ↳ INPUTS:
        - model: PasswordHistoryModel (required) - Model to save
    ↳ RETURNS: bool - True if saved successfully
    ↳ USAGE: Persist changes to disk after modifications

    create_manual_backup(backup_path=None)
    ↳ INPUTS:
        - backup_path: str (optional) - Custom backup location
    ↳ RETURNS: bool - True if backup created
    ↳ USAGE: Create point-in-time backup of password history data

3. ENCRYPTIONSERVICE - Data Security Layer
==========================================

INITIALIZATION:
    service = EncryptionService(
        client_ip='127.0.0.1'       # Optional: Client IP for encryption context
    )

KEY METHODS:

    encrypt(data)
    ↳ INPUTS:
        - data: bytes (required) - Raw data to encrypt
    ↳ RETURNS: bytes - Encrypted data
    ↳ RAISES: EncryptionException if encryption fails
    ↳ FEATURES: Uses failsafe encryption with multiple algorithm fallbacks

    decrypt(encrypted_data)
    ↳ INPUTS:
        - encrypted_data: bytes (required) - Data to decrypt
    ↳ RETURNS: bytes - Decrypted data
    ↳ RAISES: EncryptionException if decryption fails
    ↳ FEATURES: Automatically tries multiple decryption methods

4. AUDITSERVICE - Compliance and Logging Layer
==============================================

INITIALIZATION:
    service = AuditService(
        data_dir="/path/to/audit/logs"  # Required: Directory for audit logs
    )

KEY METHODS:

    log_operation_start(operation_id, operation_type, user_uuid, **context)
    ↳ INPUTS:
        - operation_id: str (required) - Unique operation identifier
        - operation_type: str (required) - Type of operation (e.g., 'password_update')
        - user_uuid: str (optional) - User performing operation 
        - company_uuid: str (optional) - Company context
        - requesting_user_uuid: str (optional) - User who initiated request
        - ip_address: str (optional) - Request IP address
        - user_agent: str (optional) - Request user agent
        - metadata: Dict (optional) - Additional context data
    ↳ RETURNS: None
    ↳ USAGE: Call at start of every significant operation

    log_operation_success(operation_id, additional_metadata=None)
    ↳ INPUTS:
        - operation_id: str (required) - Operation identifier from log_operation_start
        - additional_metadata: Dict (optional) - Additional success context
    ↳ RETURNS: None
    ↳ USAGE: Call when operation completes successfully

    log_operation_error(operation_id, error_message, additional_metadata=None)
    ↳ INPUTS:
        - operation_id: str (required) - Operation identifier from log_operation_start
        - error_message: str (required) - Description of error
        - additional_metadata: Dict (optional) - Additional error context
    ↳ RETURNS: None
    ↳ USAGE: Call when operation fails

    log_security_event(event_type, user_uuid=None, severity='medium', **context)
    ↳ INPUTS:
        - event_type: str (required) - Type of security event
        - user_uuid: str (optional) - User involved in event
        - company_uuid: str (optional) - Company context
        - severity: str (optional) - 'low', 'medium', 'high' (default: 'medium')
        - details: Dict (optional) - Event details
    ↳ RETURNS: None
    ↳ USAGE: Log security-relevant events like password reuse attempts

    get_audit_trail(company_uuid=None, user_uuid=None, start_date=None, end_date=None, operation_type=None, limit=1000)
    ↳ INPUTS:
        - company_uuid: str (optional) - Filter by company
        - user_uuid: str (optional) - Filter by user
        - start_date: str (optional) - ISO format start date
        - end_date: str (optional) - ISO format end date  
        - operation_type: str (optional) - Filter by operation type
        - limit: int (optional) - Maximum entries to return (default: 1000)
    ↳ RETURNS: List[Dict] - List of audit entries matching filters
    ↳ USAGE: Compliance reporting, security investigations

    get_operation_stats()
    ↳ INPUTS: None
    ↳ RETURNS: Dict - Performance and usage statistics
        Example return: {
            'total_operations': 1000,
            'successful_operations': 950,
            'failed_operations': 50,
            'average_duration': 125.5,
            'operations_by_type': {
                'password_update': {'count': 500, 'success_rate': 98.0, 'average_duration': 150.0}
            }
        }
    ↳ USAGE: Performance monitoring, system health checks

    get_security_summary(company_uuid=None, days=30)
    ↳ INPUTS:
        - company_uuid: str (optional) - Filter by company
        - days: int (optional) - Number of days to analyze (default: 30)
    ↳ RETURNS: Dict - Security event summary
        Example return: {
            'total_events': 15,
            'events_by_severity': {'high': 2, 'medium': 8, 'low': 5},
            'events_by_type': {'password_reuse_attempt': 10, 'invalid_access': 5},
            'recent_events': [...]  # Most recent 10 events
        }
    ↳ USAGE: Security dashboards, threat monitoring

    cleanup_old_logs(retention_days=90)
    ↳ INPUTS:
        - retention_days: int (optional) - Days to retain logs (default: 90)
    ↳ RETURNS: int - Number of log files removed
    ↳ USAGE: Scheduled maintenance to manage disk space

INTEGRATION PATTERNS:
====================

PATTERN 1: Simple Password Check
    history_service = PasswordHistoryService()
    is_reused = history_service.check_password_reuse(user_uuid, password_hash)
    if is_reused:
        raise ValueError("Password has been used recently")

PATTERN 2: Full Password Update with Audit
    history_service = PasswordHistoryService(audit_service=audit_service)
    try:
        success = history_service.update_user_password(
            user_uuid=user_id,
            company_uuid=company_id,
            new_password_hash=hashed_password,
            requesting_user_uuid=admin_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        if not success:
            return {"error": "Failed to update password"}
    except PasswordReusedException:
        return {"error": "Password has been used recently"}

PATTERN 3: Administrative Operations
    # Get company statistics
    stats = history_service.get_statistics(company_uuid=company_id)
    
    # Create backup before maintenance
    backup_success = history_service.create_backup()
    
    # Clean up orphaned data
    cleaned_count = history_service.cleanup_orphaned_histories()
    
    # Get audit trail for compliance
    audit_entries = audit_service.get_audit_trail(
        company_uuid=company_id,
        start_date="2025-01-01T00:00:00",
        operation_type="password_update"
    )

ERROR HANDLING:
===============

from Password_History.exceptions.password_exceptions import (
    PasswordReusedException,
    ValidationException,
    EncryptionException
)

try:
    result = history_service.update_user_password(...)
except PasswordReusedException as e:
    # Handle password reuse - return error to user
    logger.warning(f"Password reuse attempt: {e}")
    return {"error": "Password has been used recently"}
except ValidationException as e:
    # Handle validation errors - likely client error
    logger.error(f"Validation error: {e}")
    return {"error": "Invalid input parameters"}
except EncryptionException as e:
    # Handle encryption errors - system error
    logger.error(f"Encryption error: {e}")
    return {"error": "System error processing request"}
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error"}

PERFORMANCE CONSIDERATIONS:
==========================

1. PASSWORD HISTORY OPERATIONS:
   - check_password_reuse(): O(n) where n = user's history size (max 5-10, so effectively O(1))
   - add_password_to_history(): O(1) for adding, O(n) for cleanup if history exceeds max
   - get_company_password_histories(): O(m) where m = number of users in company

2. STORAGE OPERATIONS:
   - Uses UserStorageService with file-level caching
   - File locking ensures thread safety but may create bottlenecks
   - Consider batch operations for bulk updates

3. AUDIT OPERATIONS:
   - Uses buffered writes (100 entries) to optimize I/O
   - Background flush thread prevents blocking main operations
   - Audit queries read from files, consider indexing for large datasets

4. ENCRYPTION OPERATIONS:
   - Failsafe encryption tries multiple algorithms (performance vs reliability)
   - Consider connection pooling for high-throughput scenarios

SECURITY CONSIDERATIONS:
=======================

1. NEVER store plaintext passwords - always use strong hashing (bcrypt, Argon2)
2. All data is encrypted at rest using AES encryption
3. File operations use secure locking to prevent concurrent access issues
4. Audit logs capture security events for compliance and monitoring
5. User/company isolation prevents data leakage between organizations
6. Input validation prevents injection attacks and data corruption

DEPLOYMENT CHECKLIST:
====================

□ Set up data directories with proper permissions (750 or 700)
□ Configure audit log retention policy
□ Set up log rotation for audit files
□ Test backup and restore procedures
□ Configure monitoring for failed operations
□ Set up alerts for security events
□ Test performance under expected load
□ Verify encryption keys are properly managed
□ Set up scheduled cleanup operations
□ Document recovery procedures
"""
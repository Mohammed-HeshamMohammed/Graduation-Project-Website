"""
User utilities package for user management operations.

This package provides utilities for:
- User management and validation
- Notes management  
- Password history tracking
- Messaging services
- Privilege management
- Data backup and cleanup

ARCHITECTURE:
- UserUtils: Main orchestrator class that integrates all functionality
- UserValidator: Handles data validation and format checking
- PrivilegeManager: Manages user privileges and access control
- DataManager: Handles backups, statistics, and data cleanup
- Convenience functions: Simple interface for common operations

INTEGRATION FLOW:
UserUtils creates and manages instances of all other components, providing
a unified interface while maintaining separation of concerns.
"""

from .user_utils import UserUtils
from .validators import UserValidator
from .privilege_manager import PrivilegeManager
from .data_manager import DataManager
from .convenience import (
    create_user_utils,
    get_user_count_for_company,
    validate_user_data_simple,
    check_user_privilege,
    add_note_for_user,
    check_password_reuse,
    send_message_to_user,
    get_user_stats,
    backup_all_data,
    cleanup_old_data,
    search_company_users,
    user_exists,
    get_total_user_count,
    validate_email_format,
    get_privilege_hierarchy,
    is_valid_privilege
)

__version__ = "1.0.0"


# MAIN CLASSES DOCUMENTATION
class UserUtilsDocumentation:
    """
    UserUtils - Main utility class for user management operations
    
    INITIALIZATION:
        utils = UserUtils(storage: UserStorage)
        
    KEY METHODS:
        - get_user_count() -> int
        - user_exists(email: str) -> bool  
        - get_company_user_count(company_id: str) -> int
        - search_users_by_company(company_id, search_term, requesting_user_email, limit) -> List[Dict]
        - has_privilege(user_privileges: List[str], required_privilege: str) -> bool
        - validate_user_data(user_data: dict) -> tuple[bool, str]
        - backup_data(backup_path: str = None) -> bool
        - get_user_statistics(company_id: str = None) -> Dict[str, Any]
        - cleanup_old_data(days_old: int = 90) -> Dict[str, int]
        
    NOTES MANAGEMENT:
        - add_user_note(user_uuid, note, author_uuid, author_privileges) -> bool
        - get_user_notes(user_uuid, requesting_user_uuid, requesting_user_privileges) -> List[Dict]
        - update_note(note_id, new_content, user_uuid, author_uuid, author_privileges) -> bool
        - delete_note(note_id, user_uuid, author_uuid, author_privileges) -> bool
        
    PASSWORD HISTORY:
        - check_password_in_history(user_uuid: str, password_hash: str) -> bool
        - update_user_password(user_uuid: str, new_password_hash: str) -> bool
        - get_password_history_count(user_uuid: str) -> int
        
    MESSAGING:
        - add_message_to_user(user_uuid, message, author_uuid, message_type) -> bool
        - get_user_messages(user_uuid, requesting_user_uuid, requesting_user_privileges) -> List[Dict]
        - send_warning_to_subordinates(sender_uuid, message, target_user_uuids) -> Dict[str, Any]
        - send_disciplinary_action(sender_uuid, target_user_uuid, action_type, message, severity) -> Dict[str, Any]
    """
    pass


class UserValidatorDocumentation:
    """
    UserValidator - Handles user data validation
    
    INITIALIZATION:
        validator = UserValidator()
        
    KEY METHODS:
        - validate_user_data(user_data: dict) -> tuple[bool, str]
          Returns: (is_valid: bool, error_message: str)
          
        - validate_email_format(email: str) -> bool
        - validate_uuid_format(uuid: str) -> bool  
        - validate_company_id(company_id: str) -> bool
        - is_valid_privilege(privilege: str) -> bool
        - get_valid_privileges() -> Set[str]
        
    VALIDATION RULES:
        Required fields: ['uuid', 'email', 'password', 'full_name', 'company_id']
        Boolean fields: ['verified', 'is_logged_in', 'is_owner'] 
        Valid privileges: {'owner', 'admin', 'add', 'remove', 'manager', 'dispatcher',
                          'engineer', 'fuel_manager', 'fleet_officer', 'analyst', 'viewer'}
    """
    pass


class PrivilegeManagerDocumentation:
    """
    PrivilegeManager - Handles user privilege management and validation
    
    INITIALIZATION:
        privilege_manager = PrivilegeManager(storage: UserStorage)
        
    PRIVILEGE HIERARCHY (highest to lowest):
        ["owner", "admin", "manager", "dispatcher", "engineer", 
         "fuel_manager", "fleet_officer", "analyst", "viewer"]
        
    KEY METHODS:
        - has_privilege(user_privileges: List[str], required_privilege: str) -> bool
        - can_access_feature(user_privileges: List[str], feature: str) -> bool
        - get_user_privilege_level(user_privileges: List[str]) -> int
        - is_higher_privilege(user_privileges: List[str], target_privileges: List[str]) -> bool
        - can_manage_user(manager_privileges: List[str], target_privileges: List[str]) -> bool
        - get_manageable_privileges(user_privileges: List[str]) -> List[str]
        - get_privilege_hierarchy() -> List[str]
        - get_privilege_description(privilege: str) -> str
        - validate_privilege_assignment(assigner_privileges, target_privileges, new_privileges) -> tuple[bool, str]
        
    MANAGEMENT RULES:
        - Owners can manage anyone except other owners
        - Admins can manage anyone below admin level
        - Managers can manage anyone below manager level
        - Other privileges cannot manage users
    """
    pass


class DataManagerDocumentation:
    """
    DataManager - Handles data backup, statistics, and cleanup operations
    
    INITIALIZATION:
        data_manager = DataManager(storage, notes_manager, password_history_manager, messaging_service)
        
    KEY METHODS:
        - backup_data(backup_path: str = None) -> bool
          Creates timestamped backup if no path provided
          
        - get_user_statistics(company_id: str = None) -> Dict[str, Any]
          Returns: {
              'total_users': int,
              'verified_users': int, 
              'logged_in_users': int,
              'owners': int,
              'privilege_breakdown': Dict[str, int],
              'company_breakdown': Dict[str, int],
              'notes_stats': Dict,
              'password_history_stats': Dict,
              'message_stats': Dict
          }
          
        - cleanup_old_data(days_old: int = 90) -> Dict[str, int]
          Returns: {'cleaned_messages': int, 'cleaned_notes': int}
          
        - export_data(export_path: str, data_types: list = None) -> bool
          data_types: ['users', 'notes', 'messages', 'password_history']
          
        - get_data_size_info() -> Dict[str, Any]
          Returns size information and memory usage estimates
    """
    pass


# CONVENIENCE FUNCTIONS DOCUMENTATION
class ConvenienceFunctionsDocumentation:
    """
    Convenience functions provide simple interfaces for common operations
    
    USER OPERATIONS:
        - create_user_utils(storage: UserStorage = None) -> UserUtils
        - user_exists(email: str, storage: UserStorage = None) -> bool
        - get_total_user_count(storage: UserStorage = None) -> int
        - get_user_count_for_company(company_id: str, storage: UserStorage = None) -> int
        - search_company_users(company_id, search_term, requesting_user_email, limit, storage) -> list
        
    VALIDATION:
        - validate_user_data_simple(user_data: dict, storage: UserStorage = None) -> tuple[bool, str]
        - validate_email_format(email: str) -> bool
        
    PRIVILEGE MANAGEMENT:
        - check_user_privilege(user_privileges: List[str], required_privilege: str, storage: UserStorage = None) -> bool
        - get_privilege_hierarchy() -> list
        - is_valid_privilege(privilege: str) -> bool
        
    NOTES & MESSAGING:
        - add_note_for_user(user_uuid, note, author_uuid, author_privileges, storage) -> bool
        - send_message_to_user(user_uuid, message, author_uuid, message_type, storage) -> bool
        
    PASSWORD MANAGEMENT:
        - check_password_reuse(user_uuid: str, password_hash: str, storage: UserStorage = None) -> bool
        
    DATA MANAGEMENT:
        - get_user_stats(company_id: str = None, storage: UserStorage = None) -> dict
        - backup_all_data(backup_path: str = None, storage: UserStorage = None) -> bool
        - cleanup_old_data(days_old: int = 90, storage: UserStorage = None) -> dict
        
    USAGE PATTERN:
        Most convenience functions accept an optional storage parameter.
        If None is provided, a new UserStorage instance is created automatically.
        
        Example:
            # Simple usage
            count = get_total_user_count()
            
            # With custom storage
            my_storage = UserStorage()
            count = get_total_user_count(my_storage)
    """
    pass


__all__ = [
    # Main classes
    'UserUtils',
    'UserValidator', 
    'PrivilegeManager',
    'DataManager',
    
    # Convenience functions - User Operations
    'create_user_utils',
    'user_exists',
    'get_total_user_count',
    'get_user_count_for_company',
    'search_company_users',
    
    # Convenience functions - Validation
    'validate_user_data_simple',
    'validate_email_format',
    
    # Convenience functions - Privilege Management
    'check_user_privilege',
    'get_privilege_hierarchy',
    'is_valid_privilege',
    
    # Convenience functions - Notes & Messaging
    'add_note_for_user',
    'send_message_to_user',
    
    # Convenience functions - Password Management
    'check_password_reuse',
    
    # Convenience functions - Data Management
    'get_user_stats',
    'backup_all_data',
    'cleanup_old_data',
    
    # Documentation classes (for IDE help)
    'UserUtilsDocumentation',
    'UserValidatorDocumentation', 
    'PrivilegeManagerDocumentation',
    'DataManagerDocumentation',
    'ConvenienceFunctionsDocumentation',
]


# QUICK REFERENCE
"""
QUICK START EXAMPLES:

# Basic user operations
from user_utils import user_exists, get_total_user_count
if user_exists("user@example.com"):
    print(f"Total users: {get_total_user_count()}")

# Privilege checking  
from user_utils import check_user_privilege
if check_user_privilege(["admin"], "manager"):
    print("User has sufficient privileges")
    
# Data management
from user_utils import backup_all_data, get_user_stats
backup_all_data()
stats = get_user_stats("company123")

# Advanced usage with UserUtils class
from user_utils import UserUtils
from app.services.auth.storage import UserStorage

storage = UserStorage()
utils = UserUtils(storage)
users = utils.search_users_by_company("company123", "john", "admin@company.com")
"""
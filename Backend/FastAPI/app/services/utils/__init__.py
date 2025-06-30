from .user_utils import UserUtils
from .auth_utils import AuthUtils, UserUtils as AuthUserUtils
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
    is_valid_privilege,
    hash_password,
    verify_password,
    create_token,
    verify_token,
    generate_verification_token,
    validate_password_strength
)

__version__ = "1.0.0"

__all__ = [
    'UserUtils',
    'AuthUtils', 
    'UserValidator', 
    'PrivilegeManager',
    'DataManager',
    'create_user_utils',
    'user_exists',
    'get_total_user_count',
    'get_user_count_for_company',
    'search_company_users',
    'validate_user_data_simple',
    'validate_email_format',
    'check_user_privilege',
    'get_privilege_hierarchy',
    'is_valid_privilege',
    'add_note_for_user',
    'send_message_to_user',
    'check_password_reuse',
    'get_user_stats',
    'backup_all_data',
    'cleanup_old_data',
    'hash_password',
    'verify_password',
    'create_token',
    'verify_token',
    'generate_verification_token',
    'validate_password_strength',
    'UserUtilsDocumentation',
    'AuthUtilsDocumentation',
    'UserValidatorDocumentation', 
    'PrivilegeManagerDocumentation',
    'DataManagerDocumentation',
    'ConvenienceFunctionsDocumentation',
]
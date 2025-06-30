"""
Convenience functions for backward compatibility and easier usage.
"""

from typing import List
from app.services.storage import UserStorage
from .user_utils import UserUtils
from .auth_utils import AuthUtils


def create_user_utils(storage: UserStorage = None) -> UserUtils:
    return UserUtils(storage or UserStorage())


def get_user_count_for_company(company_id: str, storage: UserStorage = None) -> int:
    return create_user_utils(storage).get_company_user_count(company_id)


def validate_user_data_simple(user_data: dict, storage: UserStorage = None) -> tuple[bool, str]:
    return create_user_utils(storage).validate_user_data(user_data)


def check_user_privilege(user_privileges: List[str], required_privilege: str, storage: UserStorage = None) -> bool:
    return create_user_utils(storage).has_privilege(user_privileges, required_privilege)


def add_note_for_user(user_uuid: str, note: str, author_uuid: str, 
                      author_privileges: List[str], storage: UserStorage = None) -> bool:
    return create_user_utils(storage).add_user_note(user_uuid, note, author_uuid, author_privileges)


def check_password_reuse(user_uuid: str, password_hash: str, storage: UserStorage = None) -> bool:
    return create_user_utils(storage).check_password_in_history(user_uuid, password_hash)


def send_message_to_user(user_uuid: str, message: str, author_uuid: str, 
                        message_type: str = "general", storage: UserStorage = None) -> bool:
    return create_user_utils(storage).add_message_to_user(user_uuid, message, author_uuid, message_type)


def get_user_stats(company_id: str = None, storage: UserStorage = None) -> dict:
    return create_user_utils(storage).get_user_statistics(company_id)


def backup_all_data(backup_path: str = None, storage: UserStorage = None) -> bool:
    return create_user_utils(storage).backup_data(backup_path)


def cleanup_old_data(days_old: int = 90, storage: UserStorage = None) -> dict:
    return create_user_utils(storage).cleanup_old_data(days_old)


def search_company_users(company_id: str, search_term: str = "", 
                        requesting_user_email: str = None, limit: int = 50, 
                        storage: UserStorage = None) -> list:
    return create_user_utils(storage).search_users_by_company(company_id, search_term, requesting_user_email, limit)


def user_exists(email: str, storage: UserStorage = None) -> bool:
    return create_user_utils(storage).user_exists(email)


def get_total_user_count(storage: UserStorage = None) -> int:
    return create_user_utils(storage).get_user_count()


def validate_email_format(email: str) -> bool:
    from .validators import UserValidator
    return UserValidator().validate_email_format(email)


def get_privilege_hierarchy() -> list:
    from .privilege_manager import PrivilegeManager
    return PrivilegeManager(None).get_privilege_hierarchy()


def is_valid_privilege(privilege: str) -> bool:
    from .validators import UserValidator
    return UserValidator().is_valid_privilege(privilege)


# Auth utility convenience functions
def hash_password(password: str) -> str:
    return AuthUtils.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthUtils.verify_password(plain_password, hashed_password)


def create_token(data: dict, expires_minutes: int = None) -> str:
    return AuthUtils.create_token(data, expires_minutes)


def verify_token(token: str) -> dict:
    return AuthUtils.verify_token(token)


def generate_verification_token() -> str:
    return AuthUtils.generate_verification_token()


def validate_password_strength(password: str) -> bool:
    return AuthUtils.validate_password_strength(password)
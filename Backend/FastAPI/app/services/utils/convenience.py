"""
Convenience functions for backward compatibility and easier usage.

These functions provide a simpler interface for common operations
without requiring direct instantiation of the utility classes.
"""

from typing import List, Optional
from app.services.auth.storage import UserStorage
from .user_utils import UserUtils


def create_user_utils(storage: UserStorage = None) -> UserUtils:
    """
    Factory function to create UserUtils instance
    
    Args:
        storage: Optional UserStorage instance. If None, creates a new one.
        
    Returns:
        UserUtils: Configured UserUtils instance
    """
    if storage is None:
        storage = UserStorage()
    return UserUtils(storage)


def get_user_count_for_company(company_id: str, storage: UserStorage = None) -> int:
    """
    Convenience function to get user count for a specific company
    
    Args:
        company_id: Company ID to count users for
        storage: Optional UserStorage instance
        
    Returns:
        int: Number of users in the company
    """
    utils = create_user_utils(storage)
    return utils.get_company_user_count(company_id)


def validate_user_data_simple(user_data: dict, storage: UserStorage = None) -> tuple[bool, str]:
    """
    Convenience function for user data validation
    
    Args:
        user_data: User data dictionary to validate
        storage: Optional UserStorage instance
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    utils = create_user_utils(storage)
    return utils.validate_user_data(user_data)


def check_user_privilege(user_privileges: List[str], required_privilege: str, storage: UserStorage = None) -> bool:
    """
    Convenience function to check user privileges
    
    Args:
        user_privileges: List of user's privileges
        required_privilege: Required privilege to check
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if user has required privilege or higher
    """
    utils = create_user_utils(storage)
    return utils.has_privilege(user_privileges, required_privilege)


def add_note_for_user(user_uuid: str, note: str, author_uuid: str, 
                      author_privileges: List[str], storage: UserStorage = None) -> bool:
    """
    Convenience function to add a note for a user
    
    Args:
        user_uuid: UUID of the user to add note for
        note: Note content
        author_uuid: UUID of the note author
        author_privileges: List of author's privileges
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if note was added successfully
    """
    utils = create_user_utils(storage)
    return utils.add_user_note(user_uuid, note, author_uuid, author_privileges)


def check_password_reuse(user_uuid: str, password_hash: str, storage: UserStorage = None) -> bool:
    """
    Convenience function to check password reuse
    
    Args:
        user_uuid: UUID of the user
        password_hash: Hash of the password to check
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if password was used before
    """
    utils = create_user_utils(storage)
    return utils.check_password_in_history(user_uuid, password_hash)


def send_message_to_user(user_uuid: str, message: str, author_uuid: str, 
                        message_type: str = "general", storage: UserStorage = None) -> bool:
    """
    Convenience function to send a message to a user
    
    Args:
        user_uuid: UUID of the user to send message to
        message: Message content
        author_uuid: UUID of the message author
        message_type: Type of message (default: "general")
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if message was sent successfully
    """
    utils = create_user_utils(storage)
    return utils.add_message_to_user(user_uuid, message, author_uuid, message_type)


def get_user_stats(company_id: str = None, storage: UserStorage = None) -> dict:
    """
    Convenience function to get user statistics
    
    Args:
        company_id: Optional company ID to filter statistics
        storage: Optional UserStorage instance
        
    Returns:
        dict: User statistics
    """
    utils = create_user_utils(storage)
    return utils.get_user_statistics(company_id)


def backup_all_data(backup_path: str = None, storage: UserStorage = None) -> bool:
    """
    Convenience function to backup all data
    
    Args:
        backup_path: Optional specific backup path
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if backup was successful
    """
    utils = create_user_utils(storage)
    return utils.backup_data(backup_path)


def cleanup_old_data(days_old: int = 90, storage: UserStorage = None) -> dict:
    """
    Convenience function to cleanup old data
    
    Args:
        days_old: Number of days after which data is considered old
        storage: Optional UserStorage instance
        
    Returns:
        dict: Cleanup results with counts
    """
    utils = create_user_utils(storage)
    return utils.cleanup_old_data(days_old)


def search_company_users(company_id: str, search_term: str = "", 
                        requesting_user_email: str = None, limit: int = 50, 
                        storage: UserStorage = None) -> list:
    """
    Convenience function to search users within a company
    
    Args:
        company_id: Company ID to search within
        search_term: Optional search term
        requesting_user_email: Email of the user making the request
        limit: Maximum number of results to return
        storage: Optional UserStorage instance
        
    Returns:
        list: List of matching users
    """
    utils = create_user_utils(storage)
    return utils.search_users_by_company(company_id, search_term, requesting_user_email, limit)


def user_exists(email: str, storage: UserStorage = None) -> bool:
    """
    Convenience function to check if a user exists
    
    Args:
        email: Email address to check
        storage: Optional UserStorage instance
        
    Returns:
        bool: True if user exists
    """
    utils = create_user_utils(storage)
    return utils.user_exists(email)


def get_total_user_count(storage: UserStorage = None) -> int:
    """
    Convenience function to get total user count
    
    Args:
        storage: Optional UserStorage instance
        
    Returns:
        int: Total number of users
    """
    utils = create_user_utils(storage)
    return utils.get_user_count()


# Additional convenience functions for specific operations
def validate_email_format(email: str) -> bool:
    """
    Convenience function to validate email format
    
    Args:
        email: Email to validate
        
    Returns:
        bool: True if email format is valid
    """
    from .validators import UserValidator
    validator = UserValidator()
    return validator.validate_email_format(email)


def get_privilege_hierarchy() -> list:
    """
    Convenience function to get privilege hierarchy
    
    Returns:
        list: Ordered list of privileges from highest to lowest
    """
    from .privilege_manager import PrivilegeManager
    # Create with None storage since we only need hierarchy
    privilege_manager = PrivilegeManager(None)
    return privilege_manager.get_privilege_hierarchy()


def is_valid_privilege(privilege: str) -> bool:
    """
    Convenience function to check if a privilege is valid
    
    Args:
        privilege: Privilege to check
        
    Returns:
        bool: True if privilege is valid
    """
    from .validators import UserValidator
    validator = UserValidator()
    return validator.is_valid_privilege(privilege)
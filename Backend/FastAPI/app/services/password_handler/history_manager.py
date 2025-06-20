# app/services/password_handler/history_manager.py
"""
Password history management with enterprise features
"""

from fastapi import Request
from typing import Dict, Any, Union
import time
import logging

from app.services.storage import UserStorage
from app.services.utils import hash_password, verify_password
from .validators import get_audit_context
from .exceptions import PasswordHistoryError

# Import the enterprise password history system
from app.services.Password_History import (
    PasswordHistoryManager,
    PasswordReusedException,
    ValidationException,
    StorageException,
    EncryptionException,
    PasswordHistoryException
)

logger = logging.getLogger(__name__)

class PasswordHistoryService:
    """Service class for password history management"""
    
    def __init__(self):
        self.user_storage = UserStorage()
        self.password_history_manager = None
        self._initialize_password_history_manager()
    
    def _initialize_password_history_manager(self):
        """Initialize the enterprise password history manager"""
        try:
            self.password_history_manager = PasswordHistoryManager.get_instance(
                data_dir="/app/data/password_history",
                config={
                    "default_max_history": 10,  # Keep last 10 passwords
                    "cache_ttl": 3600,  # 1 hour cache
                    "audit_enabled": True,
                    "enable_encryption": True,
                    "enable_company_isolation": True
                }
            )
        except Exception as e:
            logger.error(f"Failed to initialize Password History Manager: {e}")
            self.password_history_manager = None
    
    def check_password_history_fallback(self, user: Dict[str, Any], new_password: str) -> Union[str, None]:
        """
        Fallback password history check (original implementation)
        """
        try:
            # Update password history
            if "password_history" not in user:
                user["password_history"] = []
            
            # Add current password to history if not already there
            if user["password"] not in user["password_history"]:
                user["password_history"].append(user["password"])
            
            # Limit password history to last 5 passwords
            user["password_history"] = user["password_history"][-5:]
            
            # Check if new password matches any password in history
            for old_password_hash in user["password_history"]:
                if verify_password(new_password, old_password_hash):
                    return "New password cannot be the same as any of your previous 5 passwords"
            
            return None
        except Exception as e:
            logger.error(f"Fallback password history check error: {e}")
            raise PasswordHistoryError(f"Password history check failed: {str(e)}")
    
    def update_user_password_basic(self, user: Dict[str, Any], new_password_hash: str) -> bool:
        """Basic password update without enterprise features"""
        try:
            user["password"] = new_password_hash
            user["password_changed_at"] = time.time()
            return self.user_storage.update_user(user)
        except Exception as e:
            logger.error(f"Basic password update error: {e}")
            return False

# Create singleton instance
_password_history_service = PasswordHistoryService()

async def check_password_with_history(
    user: Dict[str, Any], 
    new_password: str, 
    request: Request = None
) -> Union[str, None]:
    """
    Enhanced password history check using enterprise system
    Returns error message or None if password is acceptable
    """
    try:
        # Check if new password is the same as current password
        if verify_password(new_password, user["password"]):
            return "New password cannot be the same as current password"
        
        # If password history manager is not available, fallback to basic check
        if not _password_history_service.password_history_manager:
            return _password_history_service.check_password_history_fallback(user, new_password)
        
        # Get user identifiers
        user_uuid = user.get("uuid", user.get("id", user["email"]))
        company_uuid = user.get("company_uuid", user.get("company_id", "default_company"))
        
        # Hash the new password for checking
        new_password_hash = hash_password(new_password)
        
        # Get audit context
        audit_context = get_audit_context(request, user["email"])
        
        # Check if password exists in history using enterprise system
        is_reused = _password_history_service.password_history_manager.check_password_in_history(
            user_uuid=str(user_uuid),
            password_hash=new_password_hash,
            **audit_context
        )
        
        if is_reused:
            return "This password has been used recently. Please choose a different password."
        
        return None
        
    except PasswordHistoryException as e:
        logger.error(f"Password history check error for user {user['email']}: {e}")
        # Fallback to basic check if enterprise system fails
        return _password_history_service.check_password_history_fallback(user, new_password)
    except Exception as e:
        logger.error(f"Unexpected error in password history check: {e}")
        # Fallback to basic check
        return _password_history_service.check_password_history_fallback(user, new_password)

async def update_user_password_with_history(
    user: Dict[str, Any], 
    new_password: str, 
    request: Request = None,
    bypass_history_check: bool = False
) -> bool:
    """
    Update user password with enterprise history management
    """
    try:
        # Hash the new password
        new_password_hash = hash_password(new_password)
        
        # If password history manager is available, use enterprise system
        if _password_history_service.password_history_manager:
            user_uuid = user.get("uuid", user.get("id", user["email"]))
            company_uuid = user.get("company_uuid", user.get("company_id", "default_company"))
            
            # Get audit context
            audit_context = get_audit_context(request, user["email"])
            
            try:
                # Update password using enterprise system (includes history check)
                success = _password_history_service.password_history_manager.update_user_password(
                    user_uuid=str(user_uuid),
                    company_uuid=str(company_uuid),
                    new_password_hash=new_password_hash,
                    bypass_history_check=bypass_history_check,
                    **audit_context
                )
                
                if success:
                    # Update user object and save to storage
                    user["password"] = new_password_hash
                    user["password_changed_at"] = time.time()
                    return _password_history_service.user_storage.update_user(user)
                
                return False
                
            except PasswordReusedException:
                # This should not happen if we checked before, but handle it
                logger.warning(f"Password reuse detected during update for user {user['email']}")
                return False
            except (ValidationException, StorageException, EncryptionException) as e:
                logger.error(f"Enterprise password system error for user {user['email']}: {e}")
                # Fallback to basic update
                return _password_history_service.update_user_password_basic(user, new_password_hash)
        else:
            # Fallback to basic password update
            return _password_history_service.update_user_password_basic(user, new_password_hash)
            
    except Exception as e:
        logger.error(f"Error updating password for user {user['email']}: {e}")
        return False
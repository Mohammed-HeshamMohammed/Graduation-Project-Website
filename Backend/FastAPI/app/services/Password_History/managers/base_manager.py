# File: Password_History/managers/base_manager.py
"""Base manager with common functionality"""

import logging
import threading
import time
from functools import wraps
from typing import Dict, Any, Optional
from contextlib import contextmanager

from ..exceptions.password_exceptions import ConcurrencyException, ValidationException

logger = logging.getLogger(__name__)

def with_retry(max_attempts=3, delay=0.1):
    """Decorator for retrying operations on concurrency conflicts"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except ConcurrencyException as e:
                    if attempt == max_attempts - 1:
                        raise e
                    logger.warning(f"Retry attempt {attempt + 1} for {func.__name__}: {e}")
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

class BaseManager:
    """Base manager class with common functionality"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._operation_lock = threading.RLock()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_request_context(self, **kwargs) -> Dict[str, Any]:
        """Extract request context from kwargs for audit logging"""
        return {
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'requesting_user_uuid': kwargs.get('requesting_user_uuid')
        }
    
    def _validate_admin_access(self, admin_uuid: str, company_uuid: str, user_storage):
        """Validate admin access to company"""
        admin_user = user_storage.get_user_by_uuid(admin_uuid)
        if not admin_user:
            raise ValidationException(f"Admin user not found: {admin_uuid}")
        
        if admin_user.get('company_uuid') != company_uuid:
            raise ValidationException("Admin does not belong to target company")
        
        if not admin_user.get('is_admin', False):
            raise ValidationException("User does not have admin privileges")


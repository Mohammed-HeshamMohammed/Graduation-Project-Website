# storage_service/legacy_storage.py
"""Legacy storage service wrapper for backward compatibility"""

import logging
from typing import Dict, Any

from ...models.password_history import PasswordHistoryModel
from .user_storage import UserStorageService

logger = logging.getLogger(__name__)

class StorageService:
    """Legacy storage service wrapper for backward compatibility"""
    
    def __init__(self, data_dir: str = None, encryption_service=None):
        # encryption_service parameter is ignored in new implementation
        self.user_storage = UserStorageService(data_dir)
        logger.warning("Using legacy StorageService wrapper. Consider migrating to UserStorageService.")
    
    def load_password_history(self) -> PasswordHistoryModel:
        """Legacy method - loads empty model (migration recommended)"""
        logger.warning("load_password_history() is deprecated. Use load_user_history(user_uuid, email) instead.")
        return PasswordHistoryModel()
    
    def save_password_history(self, model: PasswordHistoryModel) -> bool:
        """Legacy method - does nothing (migration recommended)"""
        logger.warning("save_password_history() is deprecated. Use save_user_history(user_uuid, email, entries) instead.")
        return False
    
    def migrate_to_user_storage(self) -> Dict[str, Any]:
        """Helper method to migrate from old storage format"""
        return self.user_storage.migrate_from_old_storage(self)
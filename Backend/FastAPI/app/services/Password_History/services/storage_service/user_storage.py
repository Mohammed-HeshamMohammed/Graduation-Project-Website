# storage_service/user_storage.py
"""User-specific storage service for password history data with async support"""

import os
import json
import logging
import threading
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Callable, Union

from app.config import settings
from ...models.password_history import PasswordHistoryModel
from .file_manager import FileManager
from .exceptions import StorageException

logger = logging.getLogger(__name__)

class UserStorageService:
    """Thread-safe service for storing individual user password history with encryption, obfuscation, and async support"""
    
    def __init__(self, data_dir: str = None):
        self.file_manager = FileManager(data_dir)
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._async_lock = asyncio.Lock()  # Async lock for async operations
        
        # JSON optimization - cache frequently accessed data
        self._read_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size = 100
        self._cache_ttl = 300  # 5 minutes
        
        logger.info(f"UserStorageService initialized with directory: {self.file_manager.password_history_dir}")
    
    def _get_cache_key(self, user_uuid: str, email: str) -> str:
        """Generate cache key for user data"""
        return f"{user_uuid}_{email}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry.get('timestamp', 0) < self._cache_ttl
    
    def _update_cache(self, user_uuid: str, email: str, data: List[Dict[str, Any]]):
        """Update cache with new data"""
        cache_key = self._get_cache_key(user_uuid, email)
        
        # Clean up old cache entries if cache is too large
        if len(self._read_cache) >= self._cache_max_size:
            # Remove oldest entries
            sorted_cache = sorted(
                self._read_cache.items(),
                key=lambda x: x[1].get('timestamp', 0)
            )
            for old_key, _ in sorted_cache[:self._cache_max_size // 2]:
                del self._read_cache[old_key]
        
        self._read_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _get_from_cache(self, user_uuid: str, email: str) -> Union[List[Dict[str, Any]], None]:
        """Get data from cache if valid"""
        cache_key = self._get_cache_key(user_uuid, email)
        cache_entry = self._read_cache.get(cache_key)
        
        if cache_entry and self._is_cache_valid(cache_entry):
            return cache_entry['data']
        
        # Remove invalid cache entry
        if cache_entry:
            del self._read_cache[cache_key]
        
        return None
    
    def _invalidate_cache(self, user_uuid: str, email: str):
        """Invalidate cache entry for user"""
        cache_key = self._get_cache_key(user_uuid, email)
        if cache_key in self._read_cache:
            del self._read_cache[cache_key]
    
    def load_user_history(self, user_uuid: str, email: str) -> List[Dict[str, Any]]:
        """Load password history for a specific user (sync version with caching)"""
        with self._lock:
            # Try cache first
            cached_data = self._get_from_cache(user_uuid, email)
            if cached_data is not None:
                logger.debug(f"Loaded user {user_uuid} history from cache")
                return cached_data
            
            # Load from file
            data = self.file_manager.read_encrypted_file(user_uuid, email)
            
            # Update cache
            self._update_cache(user_uuid, email, data)
            
            return data
    
    async def async_load_user_history(self, user_uuid: str, email: str) -> List[Dict[str, Any]]:
        """Load password history for a specific user (async version with caching)"""
        async with self._async_lock:
            # Try cache first
            cached_data = self._get_from_cache(user_uuid, email)
            if cached_data is not None:
                logger.debug(f"Async loaded user {user_uuid} history from cache")
                return cached_data
            
            # Load from file
            data = await self.file_manager.async_read_encrypted_file(user_uuid, email)
            
            # Update cache
            self._update_cache(user_uuid, email, data)
            
            return data
    
    def save_user_history(self, user_uuid: str, email: str, entries: List[Dict[str, Any]]) -> bool:
        """Save password history for a specific user (sync version)"""
        with self._lock:
            # Invalidate cache before saving
            self._invalidate_cache(user_uuid, email)
            
            success = self.file_manager.write_encrypted_file(user_uuid, email, entries)
            
            # Update cache with new data if save was successful
            if success:
                self._update_cache(user_uuid, email, entries)
            
            return success
    
    async def async_save_user_history(self, user_uuid: str, email: str, entries: List[Dict[str, Any]]) -> bool:
        """Save password history for a specific user (async version)"""
        async with self._async_lock:
            # Invalidate cache before saving
            self._invalidate_cache(user_uuid, email)
            
            success = await self.file_manager.async_write_encrypted_file(user_uuid, email, entries)
            
            # Update cache with new data if save was successful
            if success:
                self._update_cache(user_uuid, email, entries)
            
            return success
    
    def add_password_entry(self, user_uuid: str, email: str, entry: Dict[str, Any]) -> bool:
        """Add a single password entry to user's history (sync version)"""
        def update_func(entries):
            entries.append(entry)
            return True
        
        return self.atomic_update_user(user_uuid, email, update_func)
    
    async def async_add_password_entry(self, user_uuid: str, email: str, entry: Dict[str, Any]) -> bool:
        """Add a single password entry to user's history (async version)"""
        def update_func(entries):
            entries.append(entry)
            return True
        
        return await self.async_atomic_update_user(user_uuid, email, update_func)
    
    def remove_password_entry(self, user_uuid: str, email: str, entry_id: str) -> bool:
        """Remove a password entry from user's history (sync version)"""
        def update_func(entries):
            original_length = len(entries)
            entries[:] = [e for e in entries if e.get('id') != entry_id]
            return len(entries) != original_length
        
        return self.atomic_update_user(user_uuid, email, update_func)
    
    async def async_remove_password_entry(self, user_uuid: str, email: str, entry_id: str) -> bool:
        """Remove a password entry from user's history (async version)"""
        def update_func(entries):
            original_length = len(entries)
            entries[:] = [e for e in entries if e.get('id') != entry_id]
            return len(entries) != original_length
        
        return await self.async_atomic_update_user(user_uuid, email, update_func)
    
    def atomic_update_user(self, user_uuid: str, email: str, update_func: Callable[[List[Dict[str, Any]]], bool]) -> bool:
        """
        Perform an atomic update operation on user's password history (sync version)
        
        Args:
            user_uuid: User's UUID
            email: User's email
            update_func: Function that takes a list of entries and modifies it
                        Should return True if changes were made, False otherwise
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        with self._lock:
            try:
                # Load current data (with caching)
                entries = self.load_user_history(user_uuid, email)
                
                # Create a copy for modification
                entries_copy = entries.copy()
                
                # Apply update function
                changes_made = update_func(entries_copy)
                
                # Save only if changes were made
                if changes_made:
                    return self.save_user_history(user_uuid, email, entries_copy)
                
                return True
                
            except Exception as e:
                logger.error(f"Error in atomic update for user {user_uuid}: {type(e).__name__}: {e}")
                raise StorageException(f"Atomic update failed for user {user_uuid}: {e}")
    
    async def async_atomic_update_user(self, user_uuid: str, email: str, update_func: Callable[[List[Dict[str, Any]]], bool]) -> bool:
        """
        Perform an atomic update operation on user's password history (async version)
        
        Args:
            user_uuid: User's UUID
            email: User's email
            update_func: Function that takes a list of entries and modifies it
                        Should return True if changes were made, False otherwise
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        async with self._async_lock:
            try:
                # Load current data (with caching)
                entries = await self.async_load_user_history(user_uuid, email)
                
                # Create a copy for modification
                entries_copy = entries.copy()
                
                # Apply update function
                changes_made = update_func(entries_copy)
                
                # Save only if changes were made
                if changes_made:
                    return await self.async_save_user_history(user_uuid, email, entries_copy)
                
                return True
                
            except Exception as e:
                logger.error(f"Error in async atomic update for user {user_uuid}: {type(e).__name__}: {e}")
                raise StorageException(f"Async atomic update failed for user {user_uuid}: {e}")
    
    def delete_user_history(self, user_uuid: str, email: str) -> bool:
        """Delete all password history for a specific user (sync version)"""
        with self._lock:
            # Invalidate cache
            self._invalidate_cache(user_uuid, email)
            
            return self.file_manager.delete_user_file(user_uuid, email)
    
    async def async_delete_user_history(self, user_uuid: str, email: str) -> bool:
        """Delete all password history for a specific user (async version)"""
        async with self._async_lock:
            # Invalidate cache
            self._invalidate_cache(user_uuid, email)
            
            return await self.file_manager.async_delete_user_file(user_uuid, email)
    
    def get_user_stats(self, user_uuid: str, email: str) -> Dict[str, Any]:
        """Get statistics about a user's password history (sync version)"""
        try:
            entries = self.load_user_history(user_uuid, email)
            file_stats = self.file_manager.get_file_stats(user_uuid, email)
            
            stats = {
                'entry_count': len(entries),
                **file_stats
            }
            
            if entries:
                # Calculate date range
                dates = [entry.get('created_at') for entry in entries if entry.get('created_at')]
                if dates:
                    stats['oldest_entry'] = min(dates)
                    stats['newest_entry'] = max(dates)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats for {user_uuid}: {e}")
            return {'error': str(e)}
    
    async def async_get_user_stats(self, user_uuid: str, email: str) -> Dict[str, Any]:
        """Get statistics about a user's password history (async version)"""
        try:
            entries = await self.async_load_user_history(user_uuid, email)
            file_stats = self.file_manager.get_file_stats(user_uuid, email)
            
            stats = {
                'entry_count': len(entries),
                **file_stats
            }
            
            if entries:
                # Calculate date range
                dates = [entry.get('created_at') for entry in entries if entry.get('created_at')]
                if dates:
                    stats['oldest_entry'] = min(dates)
                    stats['newest_entry'] = max(dates)
            
            return stats
        except Exception as e:
            logger.error(f"Error getting async user stats for {user_uuid}: {e}")
            return {'error': str(e)}
    
    def create_manual_backup(self, user_uuid: str, email: str, backup_path: str = None) -> bool:
        """Create a manual backup of user's password history data (sync version)"""
        with self._lock:
            try:
                if backup_path is None:
                    timestamp = int(time.time())
                    backup_file = self.file_manager.password_history_dir.parent / f"user_{user_uuid}_backup_{timestamp}.json"
                else:
                    backup_file = Path(backup_path)
                
                # Load current data
                entries = self.load_user_history(user_uuid, email)
                
                # Ensure backup directory exists
                os.makedirs(backup_file.parent, exist_ok=True)
                
                # Save as plain JSON for manual backup
                backup_data = {
                    'user_uuid': user_uuid,
                    'email': email,
                    'backup_timestamp': int(time.time()),
                    'entries': entries
                }
                
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, sort_keys=True, default=str)
                
                logger.info(f"Manual backup created for user {user_uuid} at {backup_file}")
                return True
                
            except Exception as e:
                logger.error(f"Error creating manual backup for user {user_uuid}: {type(e).__name__}: {e}")
                return False
    
    async def async_create_manual_backup(self, user_uuid: str, email: str, backup_path: str = None) -> bool:
        """Create a manual backup of user's password history data (async version)"""
        async with self._async_lock:
            try:
                if backup_path is None:
                    timestamp = int(time.time())
                    backup_file = self.file_manager.password_history_dir.parent / f"user_{user_uuid}_backup_{timestamp}.json"
                else:
                    backup_file = Path(backup_path)
                
                # Load current data
                entries = await self.async_load_user_history(user_uuid, email)
                
                # Ensure backup directory exists
                os.makedirs(backup_file.parent, exist_ok=True)
                
                # Save as plain JSON for manual backup
                backup_data = {
                    'user_uuid': user_uuid,
                    'email': email,
                    'backup_timestamp': int(time.time()),
                    'entries': entries
                }
                
                # Use async file operations
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    lambda: json.dump(backup_data, open(backup_file, 'w'), indent=2, sort_keys=True, default=str)
                )
                
                logger.info(f"Async manual backup created for user {user_uuid} at {backup_file}")
                return True
                
            except Exception as e:
                logger.error(f"Error creating async manual backup for user {user_uuid}: {type(e).__name__}: {e}")
                return False
    
    def list_user_files(self) -> List[str]:
        """List all user password history files (for maintenance/debugging)"""
        return self.file_manager.list_user_files()
    
    def cleanup_stale_locks(self) -> Dict[str, Any]:
        """Clean up stale lock files (use with caution)"""
        return self.file_manager.cleanup_stale_locks()
    
    async def async_cleanup_stale_locks(self) -> Dict[str, Any]:
        """Clean up stale lock files (async version)"""
        return await self.file_manager.async_cleanup_stale_locks()
    
    def clear_cache(self):
        """Clear the read cache"""
        with self._lock:
            self._read_cache.clear()
            logger.info("User storage cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            valid_entries = sum(1 for entry in self._read_cache.values() if self._is_cache_valid(entry))
            return {
                'total_entries': len(self._read_cache),
                'valid_entries': valid_entries,
                'invalid_entries': len(self._read_cache) - valid_entries,
                'cache_hit_ratio': getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1),
                'max_size': self._cache_max_size,
                'ttl_seconds': self._cache_ttl
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            user_files = self.list_user_files()
            total_size = 0
            
            for filename in user_files:
                file_path = self.file_manager.password_history_dir / filename
                if file_path.exists():
                    total_size += file_path.stat().st_size
            
            cache_stats = self.get_cache_stats()
            
            return {
                'total_users': len(user_files),
                'total_storage_bytes': total_size,
                'storage_directory': str(self.file_manager.password_history_dir),
                'lock_timeout': self.file_manager.lock_timeout,
                'retry_interval': self.file_manager.lock_retry_interval,
                'cache_stats': cache_stats
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {'error': str(e)}
    
    def migrate_from_old_storage(self, old_storage_service) -> Dict[str, Any]:
        """
        Migrate data from old centralized storage to new per-user storage
        
        Args:
            old_storage_service: Instance of the old StorageService
        
        Returns:
            Migration statistics
        """
        migration_stats = {
            'users_migrated': 0,
            'entries_migrated': 0,
            'errors': []
        }
        
        try:
            # Clear cache before migration
            self.clear_cache()
            
            # Load data from old storage
            old_model = old_storage_service.load_password_history()
            
            if not old_model or not hasattr(old_model, 'histories'):
                logger.info("No data to migrate from old storage")
                return migration_stats
            
            # Migrate each user's data
            for user_id, user_data in old_model.histories.items():
                try:
                    user_uuid = user_data.get('uuid', user_id)
                    email = user_data.get('email', f"user_{user_id}@unknown.com")
                    entries = user_data.get('entries', [])
                    
                    # Convert entries to the expected format if needed
                    if isinstance(entries, dict):
                        entries = list(entries.values())
                    
                    # Save to new storage
                    success = self.save_user_history(user_uuid, email, entries)
                    
                    if success:
                        migration_stats['users_migrated'] += 1
                        migration_stats['entries_migrated'] += len(entries)
                        logger.info(f"Migrated user {user_uuid} with {len(entries)} entries")
                    else:
                        migration_stats['errors'].append(f"Failed to save data for user {user_uuid}")
                        
                except Exception as e:
                    error_msg = f"Error migrating user {user_id}: {e}"
                    migration_stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Migration completed: {migration_stats['users_migrated']} users, "
                       f"{migration_stats['entries_migrated']} entries, "
                       f"{len(migration_stats['errors'])} errors")
            
        except Exception as e:
            error_msg = f"Migration failed: {e}"
            migration_stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        return migration_stats
    
    async def async_migrate_from_old_storage(self, old_storage_service) -> Dict[str, Any]:
        """
        Migrate data from old centralized storage to new per-user storage (async version)
        
        Args:
            old_storage_service: Instance of the old StorageService
        
        Returns:
            Migration statistics
        """
        migration_stats = {
            'users_migrated': 0,
            'entries_migrated': 0,
            'errors': []
        }
        
        try:
            # Clear cache before migration
            self.clear_cache()
            
            # Load data from old storage
            old_model = old_storage_service.load_password_history()
            
            if not old_model or not hasattr(old_model, 'histories'):
                logger.info("No data to migrate from old storage")
                return migration_stats
            
            # Migrate each user's data
            for user_id, user_data in old_model.histories.items():
                try:
                    user_uuid = user_data.get('uuid', user_id)
                    email = user_data.get('email', f"user_{user_id}@unknown.com")
                    entries = user_data.get('entries', [])
                    
                    # Convert entries to the expected format if needed
                    if isinstance(entries, dict):
                        entries = list(entries.values())
                    
                    # Save to new storage
                    success = await self.async_save_user_history(user_uuid, email, entries)
                    
                    if success:
                        migration_stats['users_migrated'] += 1
                        migration_stats['entries_migrated'] += len(entries)
                        logger.info(f"Async migrated user {user_uuid} with {len(entries)} entries")
                    else:
                        migration_stats['errors'].append(f"Failed to async save data for user {user_uuid}")
                        
                except Exception as e:
                    error_msg = f"Error async migrating user {user_id}: {e}"
                    migration_stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Async migration completed: {migration_stats['users_migrated']} users, "
                       f"{migration_stats['entries_migrated']} entries, "
                       f"{len(migration_stats['errors'])} errors")
            
        except Exception as e:
            error_msg = f"Async migration failed: {e}"
            migration_stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        return migration_stats
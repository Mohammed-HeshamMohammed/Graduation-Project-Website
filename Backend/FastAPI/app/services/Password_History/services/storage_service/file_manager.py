# storage_service/file_manager.py
"""File management utilities for storage service with async support"""

import os
import json
import time
import fcntl
import errno
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager, asynccontextmanager

from app.config import settings
from app.services.crypto import encrypt_with_failsafe, decrypt_with_failsafe
from app.services.crypto.obfuscation import obfuscate_data
from app.services.crypto.exceptions import CryptoException

from .exceptions import FileOperationException, LockTimeoutException, CorruptedDataException

logger = logging.getLogger(__name__)

class FileManager:
    """Handles file operations, locking, and encryption for storage service with async support"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.password_history_dir = self.data_dir / "password_history.enc"
        
        # File locking configuration
        self.lock_timeout = 30.0
        self.lock_retry_interval = 0.1
        
        # Async lock management
        self._async_locks: Dict[str, asyncio.Lock] = {}
        self._lock_cleanup_lock = asyncio.Lock()
        
        # JSON optimization cache
        self._json_decoder = json.JSONDecoder()
        self._json_encoder = json.JSONEncoder(indent=2, sort_keys=True, default=str)
        
        # Ensure directory exists
        os.makedirs(self.password_history_dir, exist_ok=True)
        
        logger.info(f"FileManager initialized with directory: {self.password_history_dir}")
    
    def generate_user_filename(self, user_uuid: str, email: str) -> str:
        """Generate obfuscated filename for user's password history"""
        try:
            unique_id = f"{user_uuid}_{email}"
            unique_bytes = unique_id.encode('utf-8')
            obfuscated_bytes = obfuscate_data(unique_bytes)
            filename_hash = hashlib.sha256(obfuscated_bytes).hexdigest()
            return f"{filename_hash}.enc"
        except Exception as e:
            logger.error(f"Error generating user filename: {e}")
            # Fallback to simpler hash
            fallback_id = f"{user_uuid}_{email}"
            return hashlib.sha256(fallback_id.encode()).hexdigest() + ".enc"
    
    def get_user_file_path(self, user_uuid: str, email: str) -> Path:
        """Get the full path to user's encrypted password history file"""
        filename = self.generate_user_filename(user_uuid, email)
        return self.password_history_dir / filename
    
    def get_lock_file_path(self, user_uuid: str, email: str) -> Path:
        """Get the lock file path for a specific user"""
        filename = self.generate_user_filename(user_uuid, email)
        return self.password_history_dir / f"{filename}.lock"
    
    def _get_lock_key(self, user_uuid: str, email: str) -> str:
        """Generate a unique lock key for async operations"""
        return f"{user_uuid}_{email}"
    
    async def _get_async_lock(self, lock_key: str) -> asyncio.Lock:
        """Get or create an async lock for a specific user"""
        async with self._lock_cleanup_lock:
            if lock_key not in self._async_locks:
                self._async_locks[lock_key] = asyncio.Lock()
            return self._async_locks[lock_key]
    
    async def _cleanup_async_lock(self, lock_key: str):
        """Clean up async lock if no longer needed"""
        async with self._lock_cleanup_lock:
            if lock_key in self._async_locks:
                lock = self._async_locks[lock_key]
                if not lock.locked():
                    del self._async_locks[lock_key]
    
    @contextmanager
    def file_lock(self, user_uuid: str, email: str, operation: str = "read"):
        """Context manager for file-level locking with timeout (sync version)"""
        lock_file_path = self.get_lock_file_path(user_uuid, email)
        lock_file = None
        acquired = False
        start_time = time.time()
        
        try:
            os.makedirs(lock_file_path.parent, exist_ok=True)
            lock_file = open(lock_file_path, 'w')
            
            lock_type = fcntl.LOCK_EX if operation == "write" else fcntl.LOCK_SH
            
            # Try to acquire lock with timeout
            while time.time() - start_time < self.lock_timeout:
                try:
                    fcntl.flock(lock_file.fileno(), lock_type | fcntl.LOCK_NB)
                    acquired = True
                    logger.debug(f"Acquired {operation} lock for user {user_uuid}")
                    break
                except IOError as e:
                    if e.errno in (errno.EAGAIN, errno.EACCES):
                        time.sleep(self.lock_retry_interval)
                        continue
                    else:
                        raise FileOperationException(f"Failed to acquire file lock: {e}")
            
            if not acquired:
                raise LockTimeoutException(f"Timeout waiting for file lock after {self.lock_timeout} seconds")
            
            yield
            
        except Exception as e:
            logger.error(f"Error in file locking for user {user_uuid}: {e}")
            raise
        finally:
            if lock_file:
                try:
                    if acquired:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                        logger.debug(f"Released {operation} lock for user {user_uuid}")
                    lock_file.close()
                    
                    # Clean up lock file
                    if lock_file_path.exists():
                        try:
                            lock_file_path.unlink()
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Error releasing file lock: {e}")
    
    @asynccontextmanager
    async def async_file_lock(self, user_uuid: str, email: str, operation: str = "read"):
        """Async context manager for file-level locking with timeout"""
        lock_key = self._get_lock_key(user_uuid, email)
        async_lock = await self._get_async_lock(lock_key)
        
        # Acquire async lock first
        async with async_lock:
            # Then acquire file system lock
            lock_file_path = self.get_lock_file_path(user_uuid, email)
            lock_file = None
            acquired = False
            start_time = time.time()
            
            try:
                os.makedirs(lock_file_path.parent, exist_ok=True)
                lock_file = open(lock_file_path, 'w')
                
                lock_type = fcntl.LOCK_EX if operation == "write" else fcntl.LOCK_SH
                
                # Try to acquire lock with timeout and async sleep
                while time.time() - start_time < self.lock_timeout:
                    try:
                        fcntl.flock(lock_file.fileno(), lock_type | fcntl.LOCK_NB)
                        acquired = True
                        logger.debug(f"Acquired async {operation} lock for user {user_uuid}")
                        break
                    except IOError as e:
                        if e.errno in (errno.EAGAIN, errno.EACCES):
                            await asyncio.sleep(self.lock_retry_interval)
                            continue
                        else:
                            raise FileOperationException(f"Failed to acquire file lock: {e}")
                
                if not acquired:
                    raise LockTimeoutException(f"Timeout waiting for file lock after {self.lock_timeout} seconds")
                
                yield
                
            except Exception as e:
                logger.error(f"Error in async file locking for user {user_uuid}: {e}")
                raise
            finally:
                if lock_file:
                    try:
                        if acquired:
                            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                            logger.debug(f"Released async {operation} lock for user {user_uuid}")
                        lock_file.close()
                        
                        # Clean up lock file
                        if lock_file_path.exists():
                            try:
                                lock_file_path.unlink()
                            except:
                                pass
                    except Exception as e:
                        logger.warning(f"Error releasing async file lock: {e}")
        
        # Clean up async lock if possible
        await self._cleanup_async_lock(lock_key)
    
    def _optimized_json_decode(self, data: str) -> List[Dict[str, Any]]:
        """Optimized JSON decoding with error handling"""
        try:
            # Use pre-configured decoder for better performance
            result = self._json_decoder.decode(data)
            
            # Validate data structure
            if not isinstance(result, list):
                logger.warning("Invalid history data format, expected list")
                return []
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise
    
    def _optimized_json_encode(self, data: List[Dict[str, Any]]) -> str:
        """Optimized JSON encoding"""
        try:
            # Use pre-configured encoder
            return self._json_encoder.encode(data)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error: {e}")
            raise
    
    def read_encrypted_file(self, user_uuid: str, email: str) -> List[Dict[str, Any]]:
        """Read and decrypt user's password history file (sync version)"""
        user_file_path = self.get_user_file_path(user_uuid, email)
        
        if not user_file_path.exists():
            logger.info(f"Password history file for user {user_uuid} does not exist")
            return []
        
        try:
            with self.file_lock(user_uuid, email, "read"):
                with open(user_file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                if not encrypted_data:
                    logger.info(f"Password history file for user {user_uuid} exists but is empty")
                    return []
                
                # Decrypt data
                decrypted_data = decrypt_with_failsafe(encrypted_data)
                
                # Optimized JSON decoding
                history_data = self._optimized_json_decode(decrypted_data.decode('utf-8'))
                
                logger.info(f"Loaded {len(history_data)} password history entries for user {user_uuid}")
                return history_data
                
        except FileNotFoundError:
            logger.warning(f"Password history file for user {user_uuid} not found")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding password history JSON for user {user_uuid}: {e}")
            self.create_backup_and_reset(user_uuid, email)
            return []
        except CryptoException as e:
            logger.error(f"Decryption error for user {user_uuid}: {e}")
            self.create_backup_and_reset(user_uuid, email)
            return []
        except Exception as e:
            logger.error(f"Error loading password history for user {user_uuid}: {type(e).__name__}: {e}")
            return []
    
    async def async_read_encrypted_file(self, user_uuid: str, email: str) -> List[Dict[str, Any]]:
        """Read and decrypt user's password history file (async version)"""
        user_file_path = self.get_user_file_path(user_uuid, email)
        
        if not user_file_path.exists():
            logger.info(f"Password history file for user {user_uuid} does not exist")
            return []
        
        try:
            async with self.async_file_lock(user_uuid, email, "read"):
                # Use async file reading
                loop = asyncio.get_event_loop()
                encrypted_data = await loop.run_in_executor(
                    None, 
                    lambda: user_file_path.read_bytes()
                )
                
                if not encrypted_data:
                    logger.info(f"Password history file for user {user_uuid} exists but is empty")
                    return []
                
                # Decrypt data in executor to avoid blocking
                decrypted_data = await loop.run_in_executor(
                    None,
                    decrypt_with_failsafe,
                    encrypted_data
                )
                
                # Optimized JSON decoding in executor
                history_data = await loop.run_in_executor(
                    None,
                    self._optimized_json_decode,
                    decrypted_data.decode('utf-8')
                )
                
                logger.info(f"Async loaded {len(history_data)} password history entries for user {user_uuid}")
                return history_data
                
        except FileNotFoundError:
            logger.warning(f"Password history file for user {user_uuid} not found")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding password history JSON for user {user_uuid}: {e}")
            await self.async_create_backup_and_reset(user_uuid, email)
            return []
        except CryptoException as e:
            logger.error(f"Decryption error for user {user_uuid}: {e}")
            await self.async_create_backup_and_reset(user_uuid, email)
            return []
        except Exception as e:
            logger.error(f"Error async loading password history for user {user_uuid}: {type(e).__name__}: {e}")
            return []
    
    def write_encrypted_file(self, user_uuid: str, email: str, entries: List[Dict[str, Any]]) -> bool:
        """Encrypt and write user's password history file (sync version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            os.makedirs(user_file_path.parent, exist_ok=True)
            
            # Optimized JSON encoding
            data_json = self._optimized_json_encode(entries)
            data_bytes = data_json.encode('utf-8')
            encrypted_data = encrypt_with_failsafe(data_bytes)
            
            with self.file_lock(user_uuid, email, "write"):
                # Create backup of existing file
                if user_file_path.exists():
                    self.create_backup(user_uuid, email)
                
                # Atomic write using temporary file
                temp_path = user_file_path.with_suffix('.tmp')
                try:
                    with open(temp_path, 'wb') as f:
                        f.write(encrypted_data)
                    
                    temp_path.replace(user_file_path)
                    logger.info(f"Saved password history for user {user_uuid} ({len(entries)} entries)")
                    return True
                    
                except Exception as write_error:
                    logger.error(f"Error writing encrypted password history for user {user_uuid}: {write_error}")
                    if temp_path.exists():
                        try:
                            temp_path.unlink()
                        except:
                            pass
                    return False
                    
        except Exception as e:
            logger.error(f"Error saving password history for user {user_uuid}: {type(e).__name__}: {e}")
            raise FileOperationException(f"Failed to save password history for user {user_uuid}: {e}")
    
    async def async_write_encrypted_file(self, user_uuid: str, email: str, entries: List[Dict[str, Any]]) -> bool:
        """Encrypt and write user's password history file (async version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            os.makedirs(user_file_path.parent, exist_ok=True)
            
            loop = asyncio.get_event_loop()
            
            # Optimized JSON encoding and encryption in executor
            data_json = await loop.run_in_executor(
                None,
                self._optimized_json_encode,
                entries
            )
            
            data_bytes = data_json.encode('utf-8')
            encrypted_data = await loop.run_in_executor(
                None,
                encrypt_with_failsafe,
                data_bytes
            )
            
            async with self.async_file_lock(user_uuid, email, "write"):
                # Create backup of existing file
                if user_file_path.exists():
                    await self.async_create_backup(user_uuid, email)
                
                # Atomic write using temporary file
                temp_path = user_file_path.with_suffix('.tmp')
                try:
                    await loop.run_in_executor(
                        None,
                        lambda: temp_path.write_bytes(encrypted_data)
                    )
                    
                    await loop.run_in_executor(
                        None,
                        lambda: temp_path.replace(user_file_path)
                    )
                    
                    logger.info(f"Async saved password history for user {user_uuid} ({len(entries)} entries)")
                    return True
                    
                except Exception as write_error:
                    logger.error(f"Error async writing encrypted password history for user {user_uuid}: {write_error}")
                    if temp_path.exists():
                        try:
                            await loop.run_in_executor(None, temp_path.unlink)
                        except:
                            pass
                    return False
                    
        except Exception as e:
            logger.error(f"Error async saving password history for user {user_uuid}: {type(e).__name__}: {e}")
            raise FileOperationException(f"Failed to async save password history for user {user_uuid}: {e}")
    
    def delete_user_file(self, user_uuid: str, email: str) -> bool:
        """Delete user's password history file (sync version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            lock_file_path = self.get_lock_file_path(user_uuid, email)
            
            with self.file_lock(user_uuid, email, "write"):
                if user_file_path.exists():
                    self.create_backup(user_uuid, email)
                    user_file_path.unlink()
                
                if lock_file_path.exists():
                    lock_file_path.unlink()
            
            logger.info(f"Deleted password history for user {user_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting password history for user {user_uuid}: {e}")
            return False
    
    async def async_delete_user_file(self, user_uuid: str, email: str) -> bool:
        """Delete user's password history file (async version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            lock_file_path = self.get_lock_file_path(user_uuid, email)
            
            async with self.async_file_lock(user_uuid, email, "write"):
                loop = asyncio.get_event_loop()
                
                if user_file_path.exists():
                    await self.async_create_backup(user_uuid, email)
                    await loop.run_in_executor(None, user_file_path.unlink)
                
                if lock_file_path.exists():
                    await loop.run_in_executor(None, lock_file_path.unlink)
            
            logger.info(f"Async deleted password history for user {user_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"Error async deleting password history for user {user_uuid}: {e}")
            return False
    
    def create_backup(self, user_uuid: str, email: str):
        """Create a backup of existing user password history file"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            if user_file_path.exists():
                timestamp = int(time.time())
                backup_path = user_file_path.with_name(f"{user_file_path.stem}_backup_{timestamp}.enc")
                backup_path.write_bytes(user_file_path.read_bytes())
                logger.debug(f"Created backup for user {user_uuid} at {backup_path}")
        except Exception as backup_error:
            logger.warning(f"Could not create backup for user {user_uuid}: {backup_error}")
    
    async def async_create_backup(self, user_uuid: str, email: str):
        """Create a backup of existing user password history file (async version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            if user_file_path.exists():
                timestamp = int(time.time())
                backup_path = user_file_path.with_name(f"{user_file_path.stem}_backup_{timestamp}.enc")
                
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, user_file_path.read_bytes)
                await loop.run_in_executor(None, backup_path.write_bytes, data)
                
                logger.debug(f"Created async backup for user {user_uuid} at {backup_path}")
        except Exception as backup_error:
            logger.warning(f"Could not create async backup for user {user_uuid}: {backup_error}")
    
    def create_backup_and_reset(self, user_uuid: str, email: str):
        """Create a backup of corrupted user data and reset to empty state"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            if user_file_path.exists():
                timestamp = int(time.time())
                corrupted_backup = user_file_path.with_name(
                    f"corrupted_{user_file_path.stem}_{timestamp}.bak"
                )
                
                with self.file_lock(user_uuid, email, "write"):
                    user_file_path.rename(corrupted_backup)
                    logger.warning(f"Corrupted password history for user {user_uuid} backed up to {corrupted_backup}")
        except Exception as e:
            logger.error(f"Failed to backup corrupted password history for user {user_uuid}: {e}")
    
    async def async_create_backup_and_reset(self, user_uuid: str, email: str):
        """Create a backup of corrupted user data and reset to empty state (async version)"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            if user_file_path.exists():
                timestamp = int(time.time())
                corrupted_backup = user_file_path.with_name(
                    f"corrupted_{user_file_path.stem}_{timestamp}.bak"
                )
                
                async with self.async_file_lock(user_uuid, email, "write"):
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        lambda: user_file_path.rename(corrupted_backup)
                    )
                    logger.warning(f"Async corrupted password history for user {user_uuid} backed up to {corrupted_backup}")
        except Exception as e:
            logger.error(f"Failed to async backup corrupted password history for user {user_uuid}: {e}")
    
    def list_user_files(self) -> List[str]:
        """List all user password history files"""
        try:
            if not self.password_history_dir.exists():
                return []
            
            files = []
            for file_path in self.password_history_dir.iterdir():
                if file_path.is_file() and file_path.suffix == '.enc' and not file_path.name.endswith('.lock'):
                    files.append(file_path.name)
            
            return sorted(files)
        except Exception as e:
            logger.error(f"Error listing user files: {e}")
            return []
    
    def get_file_stats(self, user_uuid: str, email: str) -> Dict[str, Any]:
        """Get file statistics for a user"""
        try:
            user_file_path = self.get_user_file_path(user_uuid, email)
            
            return {
                'file_exists': user_file_path.exists(),
                'file_size': user_file_path.stat().st_size if user_file_path.exists() else 0,
                'obfuscated_filename': self.generate_user_filename(user_uuid, email)
            }
        except Exception as e:
            logger.error(f"Error getting file stats for {user_uuid}: {e}")
            return {'error': str(e)}
    
    def cleanup_stale_locks(self) -> Dict[str, Any]:
        """Clean up stale lock files"""
        cleanup_stats = {
            'locks_cleaned': 0,
            'active_locks': 0,
            'errors': []
        }
        
        try:
            if not self.password_history_dir.exists():
                return cleanup_stats
            
            for lock_file in self.password_history_dir.glob("*.lock"):
                try:
                    with open(lock_file, 'w') as f:
                        try:
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                            lock_file.unlink()
                            cleanup_stats['locks_cleaned'] += 1
                            logger.info(f"Cleaned up stale lock file: {lock_file}")
                        except IOError:
                            cleanup_stats['active_locks'] += 1
                            logger.debug(f"Lock file is active: {lock_file}")
                except Exception as e:
                    error_msg = f"Error checking lock file {lock_file}: {e}"
                    cleanup_stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Error during lock cleanup: {e}"
            cleanup_stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        return cleanup_stats
    
    async def async_cleanup_stale_locks(self) -> Dict[str, Any]:
        """Clean up stale lock files (async version)"""
        cleanup_stats = {
            'locks_cleaned': 0,
            'active_locks': 0,
            'errors': []
        }
        
        try:
            if not self.password_history_dir.exists():
                return cleanup_stats
            
            loop = asyncio.get_event_loop()
            
            for lock_file in self.password_history_dir.glob("*.lock"):
                try:
                    def check_and_clean_lock():
                        with open(lock_file, 'w') as f:
                            try:
                                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                                lock_file.unlink()
                                return 'cleaned'
                            except IOError:
                                return 'active'
                    
                    result = await loop.run_in_executor(None, check_and_clean_lock)
                    
                    if result == 'cleaned':
                        cleanup_stats['locks_cleaned'] += 1
                        logger.info(f"Async cleaned up stale lock file: {lock_file}")
                    elif result == 'active':
                        cleanup_stats['active_locks'] += 1
                        logger.debug(f"Lock file is active: {lock_file}")
                        
                except Exception as e:
                    error_msg = f"Error async checking lock file {lock_file}: {e}"
                    cleanup_stats['errors'].append(error_msg)
                    logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Error during async lock cleanup: {e}"
            cleanup_stats['errors'].append(error_msg)
            logger.error(error_msg)
        
        return cleanup_stats
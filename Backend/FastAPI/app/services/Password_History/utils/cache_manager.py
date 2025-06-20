# File: Password_History/utils/cache_manager.py
"""Cache management for password history operations"""

import time
import threading
import logging
from typing import Any, Dict, Optional, Set
from collections import OrderedDict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = time.time()
        self.access_count += 1

class CacheManager:
    """Thread-safe cache manager with TTL and LRU eviction"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'sets': 0,
            'deletes': 0
        }
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"Cache manager initialized with max_size={max_size}, default_ttl={default_ttl}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._stats['misses'] += 1
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._stats['misses'] += 1
                return None
            
            # Update access info and move to end (most recently used)
            entry.touch()
            self._cache.move_to_end(key)
            self._stats['hits'] += 1
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            try:
                # Use provided TTL or default
                entry_ttl = ttl if ttl is not None else self.default_ttl
                
                # Create cache entry
                entry = CacheEntry(
                    value=value,
                    created_at=time.time(),
                    last_accessed=time.time(),
                    access_count=1,
                    ttl=entry_ttl
                )
                
                # If key exists, update it
                if key in self._cache:
                    self._cache[key] = entry
                    self._cache.move_to_end(key)
                else:
                    # Check if we need to evict
                    if len(self._cache) >= self.max_size:
                        self._evict_lru()
                    
                    self._cache[key] = entry
                
                self._stats['sets'] += 1
                return True
                
            except Exception as e:
                logger.error(f"Error setting cache entry {key}: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['deletes'] += 1
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        with self._lock:
            keys_to_delete = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self._cache[key]
                self._stats['deletes'] += 1
            
            if keys_to_delete:
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")
    
    def invalidate_user_cache(self, user_uuid: str):
        """Invalidate all cache entries for a specific user"""
        self.invalidate_pattern(user_uuid)
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._cache:
            lru_key = next(iter(self._cache))
            del self._cache[lru_key]
            self._stats['evictions'] += 1
    
    def _cleanup_expired(self):
        """Background thread to clean up expired entries"""
        while True:
            try:
                time.sleep(300)  # Check every 5 minutes
                
                with self._lock:
                    current_time = time.time()
                    expired_keys = []
                    
                    for key, entry in self._cache.items():
                        if entry.is_expired():
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self._cache[key]
                    
                    if expired_keys:
                        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                        
            except Exception as e:
                logger.error(f"Error in cache cleanup thread: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'utilization': len(self._cache) / self.max_size * 100,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self._stats['evictions'],
                'sets': self._stats['sets'],
                'deletes': self._stats['deletes']
            }
    
    def get_hit_rate(self) -> float:
        """Get current cache hit rate"""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            return (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
    
    def get_top_accessed_keys(self, limit: int = 10) -> List[Dict]:
        """Get most frequently accessed cache keys"""
        with self._lock:
            sorted_entries = sorted(
                [(key, entry) for key, entry in self._cache.items()],
                key=lambda x: x[1].access_count,
                reverse=True
            )
            
            return [
                {
                    'key': key,
                    'access_count': entry.access_count,
                    'created_at': entry.created_at,
                    'last_accessed': entry.last_accessed
                }
                for key, entry in sorted_entries[:limit]
            ]
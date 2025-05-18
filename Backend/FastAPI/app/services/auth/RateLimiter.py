# app/services/auth/RateLimiter.py
import time
from typing import Dict, List

class RateLimiter:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RateLimiter, cls).__new__(cls)
            cls._instance.store = {}
            cls._instance.last_cleanup = time.time()
            cls._instance.cleanup_interval = 3600  # Cleanup old entries every hour
        return cls._instance
    
    def check_rate_limit(self, ip_address: str, endpoint: str, limit: int = 5, window_seconds: int = 60) -> bool:
        """
        Enhanced rate limiting with automatic cleanup
        Returns True if request is allowed, False if rate limited
        """
        current_time = time.time()
        
        # Periodic cleanup of old entries
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_entries()
            self.last_cleanup = current_time
        
        # Initialize data structure if needed
        if ip_address not in self.store:
            self.store[ip_address] = {}
        
        if endpoint not in self.store[ip_address]:
            self.store[ip_address][endpoint] = []
        
        # Filter timestamps within window
        self.store[ip_address][endpoint] = [
            ts for ts in self.store[ip_address][endpoint]
            if current_time - ts < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.store[ip_address][endpoint]) >= limit:
            return False
        
        # Add current timestamp
        self.store[ip_address][endpoint].append(current_time)
        return True
    
    def _cleanup_expired_entries(self):
        """Remove expired entries to prevent memory leaks"""
        current_time = time.time()
        ips_to_remove = []
        
        for ip, endpoints in self.store.items():
            endpoints_to_remove = []
            
            for endpoint, timestamps in endpoints.items():
                # Keep only timestamps within last 24 hours
                valid_timestamps = [ts for ts in timestamps if current_time - ts < 86400]
                
                if valid_timestamps:
                    self.store[ip][endpoint] = valid_timestamps
                else:
                    endpoints_to_remove.append(endpoint)
            
            # Remove empty endpoints
            for endpoint in endpoints_to_remove:
                del self.store[ip][endpoint]
            
            # Mark empty IPs for removal
            if not self.store[ip]:
                ips_to_remove.append(ip)
        
        # Remove empty IPs
        for ip in ips_to_remove:
            del self.store[ip]

# Create a singleton instance to be imported by other modules
rate_limiter = RateLimiter()
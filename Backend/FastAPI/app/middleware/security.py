# app/middleware/security.py
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
import time
import logging
import datetime
import re
import threading
from collections import defaultdict, deque
from pathlib import Path
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Tuple, Callable

from app.services.logging_service import LoggingMiddleware

# Configure logging
logger = logging.getLogger(__name__)
log_dir = Path("logs/security")
log_dir.mkdir(parents=True, exist_ok=True)

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
MAX_OPERATIONS = 100    # max operations per window
IP_OPERATIONS = 50      # max operations per IP address per window

# Input validation constants
MAX_INPUT_SIZE = 50 * 1024 * 1024  # 50 MB
INPUT_PATTERN = re.compile(rb'^[\x00-\xFF]*$')  # Validate as binary data

# IP tracking for rate limiting (in-memory)
ip_operations = defaultdict(lambda: deque(maxlen=1000))

# Global rate limiting
operation_timestamps = deque(maxlen=MAX_OPERATIONS * 10)
rate_limit_lock = threading.RLock()

class SecurityException(Exception):
    """Base exception for all security operations"""
    pass

class InputValidationError(SecurityException):
    """Exception for input validation failures"""
    pass

class RateLimitExceeded(SecurityException):
    """Exception when rate limit is exceeded"""
    pass


def log_security_event(message, event_type):
    """
    Log security events in a simple, readable format
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = log_dir / f"security_events_{datetime.datetime.now().strftime('%Y%m%d')}.log"
    
    # Simple log format for easy reading
    log_entry = f"[{timestamp}] [{event_type}] {message}\n"
    
    # Write to log file
    with open(log_file, "a") as f:
        f.write(log_entry)
    
    # Also log to regular logger
    logger.info(f"[{event_type}] {message}")


def rate_limit(func):
    """
    Decorator for rate limiting operations
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get client IP from kwargs or use default
        client_ip = kwargs.pop('client_ip', '0.0.0.0')
        operation_name = func.__name__
        
        with rate_limit_lock:
            current_time = time.time()
            cutoff_time = current_time - RATE_LIMIT_WINDOW
            
            # Clean up expired timestamps from global tracker
            while operation_timestamps and operation_timestamps[0] < cutoff_time:
                operation_timestamps.popleft()
                
            # Clean up expired timestamps from IP tracker
            while ip_operations[client_ip] and ip_operations[client_ip][0] < cutoff_time:
                ip_operations[client_ip].popleft()
            
            # Check global rate limit
            if len(operation_timestamps) >= MAX_OPERATIONS:
                log_security_event(
                    f"Rate limit exceeded: Global limit for operation {operation_name}",
                    "RATE_LIMIT"
                )
                raise RateLimitExceeded(f"Too many operations. Please try again later.")
                
            # Check IP-based rate limit
            if len(ip_operations[client_ip]) >= IP_OPERATIONS:
                log_security_event(
                    f"Rate limit exceeded: IP {client_ip} exceeded limit for operation {operation_name}",
                    "RATE_LIMIT"
                )
                raise RateLimitExceeded(f"Too many operations from your address. Please try again later.")
            
            # Add new timestamp
            operation_timestamps.append(current_time)
            ip_operations[client_ip].append(current_time)
        
        # If everything is OK, call the original function
        return func(*args, **kwargs)
    
    return wrapper


def validate_input(data: Any, max_size: int = MAX_INPUT_SIZE) -> bytes:
    """
    Validate input data before processing
    """
    # Check if data is None
    if data is None:
        raise InputValidationError("Input data cannot be None")
    
    # Convert string data to bytes if needed
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Ensure data is bytes
    if not isinstance(data, bytes):
        try:
            data = bytes(data)
        except:
            raise InputValidationError(f"Invalid input type: {type(data)}, unable to convert to bytes")
    
    # Check size
    if len(data) > max_size:
        raise InputValidationError(f"Input data exceeds maximum size of {max_size} bytes")
    
    # Validate content (basic check that it's valid binary data)
    if not INPUT_PATTERN.match(data):
        raise InputValidationError("Input contains invalid byte patterns")
    
    return data


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers to the response
        for header_name, header_value in settings.SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
            
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log the request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log the response
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else '0.0.0.0'
        endpoint = request.url.path
        
        # Skip rate limiting for certain paths if needed
        excluded_paths = getattr(settings, 'RATE_LIMIT_EXCLUDED_PATHS', [])
        if any(re.match(pattern, endpoint) for pattern in excluded_paths):
            return await call_next(request)
        
        with rate_limit_lock:
            current_time = time.time()
            cutoff_time = current_time - RATE_LIMIT_WINDOW
            
            # Clean up expired timestamps from IP tracker
            while ip_operations[client_ip] and ip_operations[client_ip][0] < cutoff_time:
                ip_operations[client_ip].popleft()
            
            # Check IP-based rate limit
            if len(ip_operations[client_ip]) >= IP_OPERATIONS:
                log_security_event(
                    f"Rate limit exceeded: IP {client_ip} exceeded limit for endpoint {endpoint}",
                    "RATE_LIMIT"
                )
                return Response(
                    content="Rate limit exceeded. Please try again later.",
                    status_code=429,
                    media_type="text/plain"
                )
            
            # Add new timestamp
            ip_operations[client_ip].append(current_time)
        
        # If rate limit is not exceeded, continue with the request
        return await call_next(request)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate input data for specific endpoints"""
    
    async def dispatch(self, request: Request, call_next):
        # Only validate POST, PUT, PATCH requests that may contain a body
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                # Check Content-Length if available
                content_length = request.headers.get('content-length')
                if content_length and int(content_length) > MAX_INPUT_SIZE:
                    log_security_event(
                        f"Input validation failed: Content-Length {content_length} exceeds maximum size",
                        "VALIDATION_ERROR"
                    )
                    return Response(
                        content="Request entity too large",
                        status_code=413,
                        media_type="text/plain"
                    )
                
                # For endpoints that need more specific validation, we can add custom logic here
                # This is a simple example
                
            except Exception as e:
                log_security_event(
                    f"Input validation error: {str(e)}",
                    "VALIDATION_ERROR"
                )
                return Response(
                    content="Invalid input data",
                    status_code=400,
                    media_type="text/plain"
                )
        
        # Continue with the request
        return await call_next(request)


# Export our middlewares
__all__ = [
    'SecurityHeadersMiddleware',
    'RequestLoggingMiddleware',
    'RateLimitMiddleware',
    'InputValidationMiddleware',
    'LoggingMiddleware',
    'rate_limit',
    'validate_input',
    'log_security_event'
]
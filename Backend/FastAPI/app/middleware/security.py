# app/middleware/security.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
import time
import logging
from app.services.logging_service import LoggingMiddleware

logger = logging.getLogger(__name__)

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

# Export our middlewares
__all__ = [
    'SecurityHeadersMiddleware',
    'RequestLoggingMiddleware',
    'LoggingMiddleware'  # Add our new LoggingMiddleware
]
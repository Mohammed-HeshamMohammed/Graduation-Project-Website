# app/services/logging_service.py
import logging
import json
from typing import Dict, Any, Optional, List
import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

# Configure standard Python logging
logger = logging.getLogger(__name__)

# Store for frontend messages - will be cleared after being sent
# Structure: {request_id: [{"level": "info", "message": "User logged in", "timestamp": 1234567890}]}
frontend_logs = {}

def get_request_id(request: Request) -> str:
    """Generate or retrieve a unique ID for the current request"""
    if not hasattr(request.state, "request_id"):
        request.state.request_id = f"{time.time()}_{id(request)}"
    return request.state.request_id

def log_to_frontend(request: Request, level: str, message: str, data: Optional[Dict[str, Any]] = None):
    """
    Log a message that will be sent to the frontend
    
    Args:
        request: The FastAPI request object
        level: Log level (info, warning, error, success)
        message: The message to log
        data: Optional additional data to include
    """
    request_id = get_request_id(request)
    
    if request_id not in frontend_logs:
        frontend_logs[request_id] = []
    
    log_entry = {
        "level": level,
        "message": message,
        "timestamp": time.time()
    }
    
    if data:
        log_entry["data"] = data
    
    frontend_logs[request_id].append(log_entry)
    
    # Also log to server logs
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)

def info(request: Request, message: str, data: Optional[Dict[str, Any]] = None):
    """Log an info message to both server and frontend"""
    log_to_frontend(request, "info", message, data)

def warning(request: Request, message: str, data: Optional[Dict[str, Any]] = None):
    """Log a warning message to both server and frontend"""
    log_to_frontend(request, "warning", message, data)

def error(request: Request, message: str, data: Optional[Dict[str, Any]] = None):
    """Log an error message to both server and frontend"""
    log_to_frontend(request, "error", message, data)

def success(request: Request, message: str, data: Optional[Dict[str, Any]] = None):
    """Log a success message to both server and frontend"""
    log_to_frontend(request, "success", message, data)

def get_logs_for_request(request: Request) -> List[Dict[str, Any]]:
    """Get all logs for the current request"""
    request_id = get_request_id(request)
    return frontend_logs.get(request_id, [])

def clear_logs_for_request(request: Request):
    """Clear logs for the current request"""
    request_id = get_request_id(request)
    if request_id in frontend_logs:
        del frontend_logs[request_id]

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that adds logs to response headers"""
    
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
        # Get logs for this request
        logs = get_logs_for_request(request)
        
        # If we have logs and response is JSON, add them to the response
        if logs and isinstance(response, JSONResponse):
            # Get the original response data
            response_data = json.loads(response.body.decode('utf-8'))
            
            # If response_data is a dict, add logs to it
            if isinstance(response_data, dict):
                response_data["logs"] = logs
                
                # Create a new response with the logs included
                new_response = JSONResponse(
                    content=response_data,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                
                # Clear logs for this request
                clear_logs_for_request(request)
                
                return new_response
        
        # If we couldn't add logs to the response, just clear them
        clear_logs_for_request(request)
        
        return response
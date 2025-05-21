# app/services/logging_service.py
import logging
import json
import os
import time
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Store for frontend messages - will be cleared after being sent
# Structure: {request_id: [{"level": "info", "message": "User logged in", "timestamp": 1234567890}]}
frontend_logs = {}

# Dictionary to store module-specific loggers
module_loggers = {}

def ensure_log_directory(directory_name: str) -> Path:
    """
    Ensure a log directory exists and return its path
    
    Args:
        directory_name: The name of the log directory
        
    Returns:
        Path to the log directory
    """
    log_dir = Path(f"logs/{directory_name}")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def get_module_logger(module_name: str, log_to_file: bool = False) -> logging.Logger:
    """
    Get or create a logger for a specific module
    
    Args:
        module_name: Name of the module requesting a logger
        log_to_file: Whether to also log to a module-specific file
        
    Returns:
        Logger instance
    """
    if module_name in module_loggers:
        return module_loggers[module_name]
    
    # Create a new logger
    module_logger = logging.getLogger(f"app.{module_name}")
    
    # If file logging is requested
    if log_to_file:
        log_dir = ensure_log_directory(module_name)
        
        # Create a file handler that logs everything
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"{module_name}_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        module_logger.addHandler(file_handler)
    
    # Store the logger
    module_loggers[module_name] = module_logger
    
    return module_logger

def get_request_id(request: Request) -> str:
    """Generate or retrieve a unique ID for the current request"""
    if not hasattr(request.state, "request_id"):
        request.state.request_id = f"{time.time()}_{id(request)}"
    return request.state.request_id

def log_to_frontend(request: Optional[Request], level: str, message: str, data: Optional[Dict[str, Any]] = None):
    """
    Log a message that will be sent to the frontend
    
    Args:
        request: The FastAPI request object (can be None for non-request contexts)
        level: Log level (info, warning, error, success, security)
        message: The message to log
        data: Optional additional data to include
    """
    log_entry = {
        "level": level,
        "message": message,
        "timestamp": time.time()
    }
    
    if data:
        log_entry["data"] = data
    
    # Log to server logs
    if level == "error":
        logger.error(message)
    elif level == "warning" or level == "security":
        logger.warning(message)
    else:
        logger.info(message)
    
    # If we have a request, associate with frontend logs
    if request is not None:
        request_id = get_request_id(request)
        if request_id not in frontend_logs:
            frontend_logs[request_id] = []
        frontend_logs[request_id].append(log_entry)

def info(request: Optional[Request], message: str, data: Optional[Dict[str, Any]] = None):
    """Log an info message to both server and frontend"""
    log_to_frontend(request, "info", message, data)

def warning(request: Optional[Request], message: str, data: Optional[Dict[str, Any]] = None):
    """Log a warning message to both server and frontend"""
    log_to_frontend(request, "warning", message, data)

def error(request: Optional[Request], message: str, data: Optional[Dict[str, Any]] = None):
    """Log an error message to both server and frontend"""
    log_to_frontend(request, "error", message, data)

def success(request: Optional[Request], message: str, data: Optional[Dict[str, Any]] = None):
    """Log a success message to both server and frontend"""
    log_to_frontend(request, "success", message, data)

def security_log(
    event_type: str, 
    message: str, 
    request: Optional[Request] = None, 
    module: Optional[str] = None, 
    data: Optional[Dict[str, Any]] = None
):
    """
    Log a security-related event
    
    Args:
        event_type: Type of security event (e.g., "ENCRYPTION", "KEY_ROTATION")
        message: The message to log
        request: Optional FastAPI request object
        module: Optional module name for module-specific logging
        data: Optional additional data to include
    """
    # Create a specialized security log entry
    log_entry = {
        "level": "security",
        "event_type": event_type,
        "message": message,
        "timestamp": time.time()
    }
    
    if data:
        # Ensure sensitive data is not logged
        safe_data = {
            k: v for k, v in data.items() 
            if k not in ("key", "password", "token", "secret")
        }
        log_entry["data"] = safe_data
    
    # Log to server logs
    security_message = f"SECURITY: {event_type} - {message}"
    logger.warning(security_message)
    
    # If module is specified, log to module-specific logger
    if module:
        module_logger = get_module_logger(module, log_to_file=True)
        module_logger.warning(security_message)
    
    # If we have a request, associate with frontend logs
    if request:
        request_id = get_request_id(request)
        if request_id not in frontend_logs:
            frontend_logs[request_id] = []
        frontend_logs[request_id].append(log_entry)
    
    # Always log security events to a dedicated security log file
    security_logger = get_module_logger("security", log_to_file=True)
    security_logger.warning(security_message)

def get_logs_for_request(request: Request) -> List[Dict[str, Any]]:
    """Get all logs for the current request"""
    request_id = get_request_id(request)
    return frontend_logs.get(request_id, [])

def clear_logs_for_request(request: Request):
    """Clear logs for the current request"""
    request_id = get_request_id(request)
    if request_id in frontend_logs:
        del frontend_logs[request_id]

def log_exception(
    exc: Exception, 
    request: Optional[Request] = None, 
    module: Optional[str] = None, 
    context: Optional[Dict[str, Any]] = None
):
    """
    Log an exception with detailed information
    
    Args:
        exc: The exception to log
        request: Optional FastAPI request object
        module: Optional module name for module-specific logging
        context: Optional additional context information
    """
    exception_data = {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "timestamp": time.time()
    }
    
    if context:
        exception_data["context"] = context
    
    # Create message
    message = f"Exception: {type(exc).__name__}: {str(exc)}"
    
    # Log to main logger
    logger.exception(message)
    
    # If module is specified, log to module-specific logger
    if module:
        module_logger = get_module_logger(module, log_to_file=True)
        module_logger.exception(message)
    
    # If request is available, add to frontend logs
    if request:
        log_entry = {
            "level": "error",
            "message": message,
            "timestamp": time.time(),
            "data": exception_data
        }
        request_id = get_request_id(request)
        if request_id not in frontend_logs:
            frontend_logs[request_id] = []
        frontend_logs[request_id].append(log_entry)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that adds logs to response headers"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request start
        info(request, f"Request started: {request.method} {request.url.path}")
        
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log request completion
            info(
                request, 
                f"Request completed: {request.method} {request.url.path}",
                {"status_code": response.status_code, "duration": duration}
            )
            
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
            
        except Exception as exc:
            # Log exception
            log_exception(exc, request, context={"path": request.url.path, "method": request.method})
            
            # Re-raise the exception to be handled by FastAPI
            raise
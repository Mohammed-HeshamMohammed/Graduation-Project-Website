# app/services/auth/user_status.py
from fastapi import Request, HTTPException
from typing import Dict, Any
import logging
import traceback

from app.services.auth.utils import verify_token
from app.services.auth.storage import UserStorage
from app.services.auth import logging_service

# Configure logging
logger = logging.getLogger(__name__)
user_storage = UserStorage()

async def check_login_status(token: str = None, request: Request = None) -> Dict[str, Any]:
    """
    Check if a user is logged in by validating their token
    
    Args:
        token: The JWT token to validate
        request: The FastAPI request object for logging
        
    Returns:
        Dict containing login status and user info if logged in
    """
    if not token:
        if request:
            logging_service.info(request, "Status check - no token provided")
        return {"is_logged_in": False}
    
    try:
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            if request:
                logging_service.info(request, f"Status check failed - token error: {payload['error']}")
            return {"is_logged_in": False, "error": payload["error"]}
        
        email = payload.get("sub")
        if not email:
            if request:
                logging_service.info(request, "Status check failed - no email in token")
            return {"is_logged_in": False}
        
        user = user_storage.get_user_by_email(email)
        if not user or not user.get("verified", False):
            if request:
                logging_service.info(request, f"Status check failed - user not found or not verified: {email}")
            return {"is_logged_in": False}
        
        if request:
            logging_service.info(request, f"Status check successful for user: {email}")
        
        return {
            "is_logged_in": True,
            "email": email,
            "full_name": user.get("full_name"),
            "company_name": user.get("company_name")
        }
    except Exception as e:
        if request:
            logging_service.error(request, f"Status check error: {str(e)}")
        logger.error(f"Status check error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"is_logged_in": False, "error": "Token verification failed"}

async def perform_logout(request: Request = None) -> Dict[str, str]:
    """
    Perform user logout - mostly just for logging purposes
    
    Args:
        request: The FastAPI request object for logging
        
    Returns:
        Success message dictionary
    """
    if request:
        logging_service.info(request, "User logged out")
    return {"message": "Logged out successfully"}
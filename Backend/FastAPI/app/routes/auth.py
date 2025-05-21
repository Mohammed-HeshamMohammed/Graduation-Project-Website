# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Request, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any
import logging
import traceback
from fastapi import BackgroundTasks

# Use relative imports for better compatibility
from app.models.user_models import UserRegister, UserLogin, UserResponse
from app.services.auth.storage import UserStorage
from app.services.email_utils import send_verification_email
from app.services.utils import verify_token
from app.services import logging_service
from app.services.auth.RateLimiter import rate_limiter
from app.services.auth.authentication_forms import register, verify, login
from app.services.auth.password_handler import (
    forgot_password, 
    reset_password_form, 
    reset_password_confirm, 
    change_password
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
user_storage = UserStorage()

# Register the imported route handlers
router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)(register)
router.get("/verify", response_class=HTMLResponse)(verify)
router.post("/login", response_model=UserResponse)(login)

# Register password management route handlers
router.post("/forgot-password")(forgot_password)
router.get("/reset-password", response_class=HTMLResponse)(reset_password_form)
router.post("/reset-password-confirm", response_class=HTMLResponse)(reset_password_confirm)
router.post("/change-password")(change_password)

@router.get("/status")
async def check_login_status(token: str = Query(None), request: Request = None):
    """
    Check if a user is logged in by validating their token
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
            "full_name": user.get("full_name")
        }
    except Exception as e:
        if request:
            logging_service.error(request, f"Status check error: {str(e)}")
        logger.error(f"Status check error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"is_logged_in": False, "error": "Token verification failed"}


@router.post("/logout")
async def logout(request: Request = None):
    """
    No server-side logout is needed for JWT tokens,
    but we provide this endpoint for front-end consistency
    """
    if request:
        logging_service.info(request, "User logged out")
    return {"message": "Logged out successfully"}
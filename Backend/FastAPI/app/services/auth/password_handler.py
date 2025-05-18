# app/services/auth/password_handler.py
from fastapi import HTTPException, Request, Form, status, BackgroundTasks, Query
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Union
import time
import logging
import traceback

from app.services.auth.storage import UserStorage
from app.services.auth.email_utils import send_verification_email, send_password_reset_email
from app.services.auth.utils import hash_password, verify_password, create_token, verify_token, validate_password_strength
from app.services.auth import logging_service
from app.services.auth.RateLimiter import rate_limiter  # Import the singleton instance
from app.services.auth.auth_templates import HTML_TEMPLATES, get_reset_password_form  # Import HTML templates

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
# Don't recreate the rate limiter here, use the singleton instance

# Reusable password history functions
def check_password_history(user: Dict[str, Any], new_password: str) -> Union[str, None]:
    """
    Check if new password is in user's password history
    Returns error message or None if password is acceptable
    """
    # Check if new password is the same as current password
    if verify_password(new_password, user["password"]):
        return "New password cannot be the same as current password"
    
    # Update password history
    if "password_history" not in user:
        user["password_history"] = []
    
    # Add current password to history if not already there
    if user["password"] not in user["password_history"]:
        user["password_history"].append(user["password"])
    
    # Limit password history to last 5 passwords
    user["password_history"] = user["password_history"][-5:]
    
    # Check if new password matches any password in history
    for old_password_hash in user["password_history"]:
        if verify_password(new_password, old_password_hash):
            return "New password cannot be the same as any of your previous 5 passwords"
    
    return None

def update_user_password(user: Dict[str, Any], new_password: str) -> bool:
    """Update user password and related fields"""
    user["password"] = hash_password(new_password)
    user["password_changed_at"] = time.time()
    return user_storage.update_user(user)

# Token validation helper
def validate_token(token: str, token_type: str = None) -> Dict[str, Any]:
    """
    Validate token and return payload or raise appropriate HTTPException
    """
    payload = verify_token(token)
    
    # Check for token errors
    if "error" in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {payload['error']}"
        )
    
    # Verify token type if specified
    if token_type and payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid token type: expected {token_type}"
        )
    
    return payload

async def forgot_password(
    email: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Send password reset link to user's email
    """
    # Rate limiting check
    client_ip = request.client.host
    if not rate_limiter.check_rate_limit(client_ip, "forgot_password", 3, 300):  # 3 requests per 5 minutes
        logging_service.warning(request, f"Rate limit exceeded for password reset from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Please try again later."
        )
    
    try:
        logging_service.info(request, f"Password reset request for email: {email}")
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            # For security reasons, don't reveal if email exists
            logging_service.info(request, f"Password reset for non-existent email: {email}")
            return {"message": "If your email is registered, you will receive a password reset link"}
        
        # Check if user is verified
        if not user.get("verified", False):
            logging_service.info(request, f"Password reset for unverified email: {email}")
            # Send verification email instead
            token = create_token({"email": email, "type": "verification"}, 1440)  # 24 hours
            await send_verification_email(email, token)
            return {"message": "Your account is not verified. A verification email has been sent instead."}
        
        # Generate password reset token (valid for 1 hour)
        reset_token = create_token({"email": email, "type": "password_reset"}, 60)
        
        # Send password reset email in background
        background_tasks.add_task(send_password_reset_email, email, reset_token)
        
        logging_service.success(request, f"Password reset email sent to: {email}")
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    except Exception as e:
        logging_service.error(request, f"Password reset error: {str(e)}")
        logger.error(traceback.format_exc())
        # Return generic message to avoid revealing if email exists
        return {"message": "If your email is registered, you will receive a password reset link"}

async def reset_password_form(token: str = Query(...), request: Request = None):
    """
    Display password reset form for valid tokens
    """
    try:
        try:
            payload = validate_token(token, "password_reset")
        except HTTPException as e:
            # Convert HTTP exception to HTML response
            return HTMLResponse(f"<h1>Password Reset Failed</h1><p>{e.detail}</p>", status_code=e.status_code)
        
        email = payload.get("email")
        if not email:
            if request:
                logging_service.warning(request, "Missing email in password reset token")
            return HTMLResponse("<h1>Invalid password reset link</h1>", status_code=400)
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"Password reset - user not found: {email}")
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Form to reset password
        return HTMLResponse(get_reset_password_form(token))
    except Exception as e:
        if request:
            logging_service.error(request, f"Password reset form error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse("<h1>Error Displaying Password Reset Form</h1>", status_code=500)

async def reset_password_confirm(
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    request: Request = None
):
    """
    Process the password reset form submission
    """
    try:
        # Verify passwords match
        if new_password != confirm_password:
            if request:
                logging_service.warning(request, "Password reset failed - passwords don't match")
            return HTMLResponse("<h1>Passwords do not match</h1>", status_code=400)
        
        # Verify password strength
        if not validate_password_strength(new_password):
            if request:
                logging_service.warning(request, "Password reset failed - password too weak")
            return HTMLResponse("<h1>Password does not meet strength requirements</h1>", status_code=400)
        
        try:
            payload = validate_token(token, "password_reset")
        except HTTPException as e:
            return HTMLResponse(f"<h1>Password Reset Failed</h1><p>{e.detail}</p>", status_code=e.status_code)
        
        email = payload.get("email")
        if not email:
            if request:
                logging_service.warning(request, "Missing email in password reset token")
            return HTMLResponse("<h1>Invalid password reset link</h1>", status_code=400)
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"Password reset - user not found: {email}")
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Check password history
        history_error = check_password_history(user, new_password)
        if history_error:
            if request:
                logging_service.warning(request, f"Password reset - {history_error}: {email}")
            return HTMLResponse(f"<h1>{history_error}</h1>", status_code=400)
        
        # Update password
        update_success = update_user_password(user, new_password)
        
        if not update_success:
            if request:
                logging_service.error(request, f"Failed to save new password for user: {email}")
            return HTMLResponse("<h1>Failed to update password</h1>", status_code=500)
        
        if request:
            logging_service.success(request, f"Password reset successful for user: {email}")
        
        return HTMLResponse(HTML_TEMPLATES["password_reset_success"])
    except Exception as e:
        if request:
            logging_service.error(request, f"Password reset confirm error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse("<h1>Error Resetting Password</h1>", status_code=500)

async def change_password(
    current_password: str, 
    new_password: str,
    token: str = Query(...),
    request: Request = None,
):
    """
    Change user password with verification of current password
    """
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            if request:
                logging_service.warning(request, f"Password change failed - token error: {payload['error']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        email = payload.get("sub")
        if not email:
            if request:
                logging_service.warning(request, "Password change failed - no email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        if request:
            logging_service.info(request, f"Password change attempt for user: {email}")
        
        # Get user
        user = user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"Password change failed - user not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user["password"]):
            if request:
                logging_service.warning(request, f"Password change failed - incorrect current password: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        if not validate_password_strength(new_password):
            if request:
                logging_service.warning(request, f"Password change failed - weak new password: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
            )
        
        # Check password history
        history_error = check_password_history(user, new_password)
        if history_error:
            if request:
                logging_service.warning(request, f"Password change failed - {history_error}: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=history_error
            )
        
        # Update password
        update_success = update_user_password(user, new_password)
        
        if not update_success:
            if request:
                logging_service.error(request, f"Failed to save new password for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )
        
        if request:
            logging_service.success(request, f"Password changed successfully for user: {email}")
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        if request:
            logging_service.error(request, f"Change password error: {str(e)}")
        logger.error(f"Change password error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )
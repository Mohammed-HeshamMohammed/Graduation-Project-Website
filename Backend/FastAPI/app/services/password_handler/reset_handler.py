# app/services/password_handler/reset_handler.py
"""
Password reset functionality
"""

from fastapi import HTTPException, Request, Form, status, BackgroundTasks, Query
from fastapi.responses import HTMLResponse
import logging
import traceback
import os
from pathlib import Path

from app.services.storage import UserStorage
from app.services.email_utils import send_verification_email, send_password_reset_email
from app.services.utils import create_token
from app.services import logging_service
from app.services.auth.RateLimiter import rate_limiter

from .validators import validate_token, validate_password_strength, validate_password_match
from .history_manager import check_password_with_history, update_user_password_with_history
from .exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)

class PasswordResetHandler:
    """Handler for password reset operations"""
    
    def __init__(self):
        self.user_storage = UserStorage()
        self.templates_dir = Path(__file__).parent.parent.parent / "templates" / "auth"
    
    def load_template(self, template_name: str, **kwargs) -> str:
        """Load HTML template from file and replace placeholders"""
        template_path = self.templates_dir / template_name
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace placeholders with provided kwargs
            for key, value in kwargs.items():
                template_content = template_content.replace(f"{{{key}}}", str(value))
            
            return template_content
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            return f"<h1>Template Error</h1><p>Template {template_name} not found</p>"
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return f"<h1>Template Error</h1><p>Error loading template: {str(e)}</p>"

# Create singleton instance
_reset_handler = PasswordResetHandler()

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
        user = _reset_handler.user_storage.get_user_by_email(email)
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
        user = _reset_handler.user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"Password reset - user not found: {email}")
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Load reset password form template
        form_html = _reset_handler.load_template("reset_password_form.html", token=token)
        return HTMLResponse(form_html)
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
        try:
            validate_password_match(new_password, confirm_password)
        except Exception:
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
        user = _reset_handler.user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"Password reset - user not found: {email}")
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Check password history with enterprise system
        history_error = await check_password_with_history(user, new_password, request)
        if history_error:
            if request:
                logging_service.warning(request, f"Password reset - {history_error}: {email}")
            return HTMLResponse(f"<h1>{history_error}</h1>", status_code=400)
        
        # Update password with enterprise system
        update_success = await update_user_password_with_history(user, new_password, request)
        
        if not update_success:
            if request:
                logging_service.error(request, f"Failed to save new password for user: {email}")
            return HTMLResponse("<h1>Failed to update password</h1>", status_code=500)
        
        if request:
            logging_service.success(request, f"Password reset successful for user: {email}")
        
        # Load success template
        success_html = _reset_handler.load_template("password_reset_success.html")
        return HTMLResponse(success_html)
    except Exception as e:
        if request:
            logging_service.error(request, f"Password reset confirm error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse("<h1>Error Resetting Password</h1>", status_code=500)
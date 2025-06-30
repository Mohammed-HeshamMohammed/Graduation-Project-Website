# app/services/password_handler/change_handler.py
"""
Password change functionality
"""

from fastapi import HTTPException, Request, status, Query
import logging
import traceback

from app.services.storage import UserStorage
from app.services.utils.auth_utils import verify_password, verify_token
from app.services import logging_service

from .validators import validate_password_strength
from .history_manager import check_password_with_history, update_user_password_with_history
from .exceptions import UserNotFoundError, PasswordValidationError

logger = logging.getLogger(__name__)

class PasswordChangeHandler:
    """Handler for password change operations"""
    
    def __init__(self):
        self.user_storage = UserStorage()

# Create singleton instance
_change_handler = PasswordChangeHandler()

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
        user = _change_handler.user_storage.get_user_by_email(email)
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
        
        # Check password history with enterprise system
        history_error = await check_password_with_history(user, new_password, request)
        if history_error:
            if request:
                logging_service.warning(request, f"Password change failed - {history_error}: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=history_error
            )
        
        # Update password with enterprise system
        update_success = await update_user_password_with_history(user, new_password, request)
        
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
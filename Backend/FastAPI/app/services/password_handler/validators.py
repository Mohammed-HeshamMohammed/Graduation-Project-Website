# app/services/password_handler/validators.py
from fastapi import HTTPException, Request, status
from typing import Dict, Any
import logging

# Updated import to use the class method properly
from app.services.utils.auth_utils import verify_token, AuthUtils
from .exceptions import TokenValidationError, PasswordValidationError

logger = logging.getLogger(__name__)

def get_audit_context(request: Request, user_email: str = None) -> Dict[str, Any]:
    """Extract audit context from request"""
    return {
        "ip_address": getattr(request.client, 'host', 'unknown') if request else 'unknown',
        "user_agent": request.headers.get('user-agent', 'unknown') if request else 'unknown',
        "requesting_user_uuid": user_email  # Using email as identifier for now
    }

def validate_token(token: str, token_type: str = None) -> Dict[str, Any]:
    """
    Validate token and return payload or raise appropriate HTTPException
    """
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise TokenValidationError(f"Token validation failed: {str(e)}")

def validate_password_strength(password: str) -> bool:
    """
    Validate password strength using utility function
    """
    try:
        # Use the static method from AuthUtils class
        return AuthUtils.validate_password_strength(password)
    except Exception as e:
        logger.error(f"Password strength validation error: {e}")
        raise PasswordValidationError(f"Password validation failed: {str(e)}")

def validate_password_match(password: str, confirm_password: str) -> bool:
    """
    Validate that passwords match
    """
    if password != confirm_password:
        raise PasswordValidationError("Passwords do not match")
    return True
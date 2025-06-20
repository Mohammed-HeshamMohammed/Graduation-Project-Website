# app/services/password_handler/__init__.py
"""
Password Handler Module

This module provides comprehensive password management functionality including:
- Password reset and change operations
- Password history management with enterprise features
- Password validation and strength checking
- Administrative functions for password management

USAGE EXAMPLES:
--------------

1. PASSWORD RESET FLOW:
   # Step 1: User requests password reset
   result = await forgot_password(
       email="user@example.com",
       request=request,
       background_tasks=background_tasks
   )
   # Returns: {"message": "If your email is registered, you will receive a password reset link"}
   
   # Step 2: User clicks link, sees form
   response = await reset_password_form(token="reset_token_here", request=request)
   # Returns: HTMLResponse with password reset form
   
   # Step 3: User submits new password
   result = await reset_password_confirm(
       token="reset_token_here",
       new_password="NewSecurePass123!",
       confirm_password="NewSecurePass123!",
       request=request
   )
   # Returns: HTMLResponse with success message

2. PASSWORD CHANGE:
   result = await change_password(
       current_password="OldPassword123!",
       new_password="NewSecurePass123!",
       token="user_auth_token",
       request=request
   )
   # Returns: {"message": "Password changed successfully"}

3. ADMIN FUNCTIONS:
   # Get user password history stats
   stats = await get_user_password_history_stats(
       user_email="user@example.com",
       request=request
   )
   # Returns: {
   #     "user_email": "user@example.com",
   #     "password_history_count": 5,
   #     "last_password_change": 1640995200.0
   # }
   
   # Clear user password history (admin only)
   result = await admin_clear_user_password_history(
       target_user_email="user@example.com",
       admin_user_email="admin@example.com",
       request=request
   )
   # Returns: {"message": "Password history cleared for user user@example.com"}
   
   # Get security summary
   summary = await get_password_security_summary(
       company_uuid="company-123",
       admin_user_email="admin@example.com",
       days=30,
       request=request
   )

4. DIRECT HISTORY MANAGEMENT:
   # Check if password conflicts with history
   error = await check_password_with_history(user_dict, "new_password", request)
   # Returns: None if OK, or error string if password conflicts
   
   # Update password with history tracking
   success = await update_user_password_with_history(user_dict, "new_password", request)
   # Returns: True if successful, False if failed

5. VALIDATION FUNCTIONS:
   # Validate token
   try:
       payload = validate_token("token_string", "password_reset")
       # Returns: {"email": "user@example.com", "type": "password_reset", ...}
   except HTTPException as e:
       # Handle invalid token
   
   # Check password strength
   is_strong = validate_password_strength("MyPassword123!")
   # Returns: True if strong, False if weak
   
   # Get audit context for logging
   context = get_audit_context(request, "user@example.com")
   # Returns: {"ip_address": "192.168.1.1", "user_agent": "...", "requesting_user_uuid": "user@example.com"}

ERROR HANDLING:
--------------
All functions may raise these custom exceptions:
- PasswordHandlerException: Base exception
- PasswordValidationError: Password doesn't meet requirements
- PasswordHistoryError: History system errors
- TokenValidationError: Invalid or expired tokens
- UserNotFoundError: User doesn't exist
- RateLimitExceededError: Too many attempts

Most functions also raise FastAPI HTTPExceptions with appropriate status codes.

EXPECTED INPUTS:
---------------
- email: Valid email string
- password: String meeting strength requirements (8+ chars, upper/lower/digits/symbols)
- token: JWT token string from authentication system
- request: FastAPI Request object (optional but recommended for logging)
- user_dict: User dictionary from UserStorage.get_user_by_email()

EXPECTED OUTPUTS:
----------------
- Success responses: Dictionary with "message" key
- Error responses: Dictionary with "error" key
- HTML responses: HTMLResponse objects for web forms
- Validation functions: Boolean or raise exceptions
- Admin functions: Dictionary with relevant data

ENTERPRISE FEATURES:
-------------------
- Password history tracking (configurable depth)
- Company-level password policies
- Audit logging with IP/user agent tracking
- Rate limiting on sensitive operations
- Encrypted password history storage
- Admin functions for bulk operations

DEPENDENCIES:
------------
- FastAPI framework
- Enterprise Password History system
- UserStorage for user management
- Email utilities for notifications
- Rate limiting system
- Logging service
"""

from .exceptions import (
    PasswordHandlerException,
    PasswordValidationError,
    PasswordHistoryError,
    TokenValidationError,
    UserNotFoundError,
    RateLimitExceededError
)

from .validators import (
    validate_token,
    validate_password_strength,
    get_audit_context
)

from .history_manager import (
    PasswordHistoryService,
    check_password_with_history,
    update_user_password_with_history
)

from .reset_handler import (
    forgot_password,
    reset_password_form,
    reset_password_confirm
)

from .change_handler import change_password

from .admin_handler import (
    get_user_password_history_stats,
    admin_clear_user_password_history,
    get_password_security_summary,
    bulk_password_policy_update,
    get_company_password_metrics
)

# Main exports
__all__ = [
    # Exceptions
    'PasswordHandlerException',
    'PasswordValidationError', 
    'PasswordHistoryError',
    'TokenValidationError',
    'UserNotFoundError',
    'RateLimitExceededError',
    
    # Validators
    'validate_token',
    'validate_password_strength',
    'get_audit_context',
    
    # History Management
    'PasswordHistoryService',
    'check_password_with_history',
    'update_user_password_with_history',
    
    # Password Reset Flow
    'forgot_password',              # Send reset email
    'reset_password_form',          # Display reset form
    'reset_password_confirm',       # Process reset form
    
    # Password Change
    'change_password',              # Change password with current password verification
    
    # Admin Functions
    'get_user_password_history_stats',      # Get user history statistics
    'admin_clear_user_password_history',    # Clear user password history
    'get_password_security_summary',        # Get security metrics
    'bulk_password_policy_update',          # Update company password policies
    'get_company_password_metrics'          # Get company-wide password metrics
]

# Module version
__version__ = '1.0.0'

# Configuration notes for developers
"""
SETUP REQUIREMENTS:
1. Ensure enterprise Password History system is properly configured
2. Set up email service for password reset notifications
3. Configure rate limiting parameters
4. Set up proper logging configuration
5. Ensure UserStorage is properly initialized

INTEGRATION NOTES:
- All functions expect FastAPI Request objects for proper logging
- Rate limiting is automatically applied to sensitive operations
- Enterprise password history system provides fallback to basic functionality
- All operations are logged with appropriate security context
"""
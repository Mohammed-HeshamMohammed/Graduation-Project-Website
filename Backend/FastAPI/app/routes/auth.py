# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Request, Response, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from typing import Optional
import time
import logging
import traceback
from pydantic import ValidationError
import uuid


# Use relative imports for better compatibility
from app.models.user_models import UserRegister, UserLogin, UserResponse
from app.services.storage import UserStorage
from app.services.crypto import encrypt_data, decrypt_data
from app.services.email_utils import send_verification_email, send_password_reset_email
from app.services.utils import hash_password, verify_password, create_token, verify_token, validate_password_strength
from app.config import settings
from app.services import logging_service
# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
user_storage = UserStorage()

# Rate limiting dictionary {ip_address: {endpoint: [timestamps]}}
rate_limit_store = {}

def check_rate_limit(ip_address: str, endpoint: str, limit: int = 5, window_seconds: int = 60) -> bool:
    """
    Basic rate limiting implementation
    Returns True if request is allowed, False if rate limited
    """
    current_time = time.time()
    
    # Initialize rate limit data structure if needed
    if ip_address not in rate_limit_store:
        rate_limit_store[ip_address] = {}
    
    if endpoint not in rate_limit_store[ip_address]:
        rate_limit_store[ip_address][endpoint] = []
    
    # Clean up old timestamps
    rate_limit_store[ip_address][endpoint] = [
        ts for ts in rate_limit_store[ip_address][endpoint]
        if current_time - ts < window_seconds
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[ip_address][endpoint]) >= limit:
        return False
    
    # Add current timestamp
    rate_limit_store[ip_address][endpoint].append(current_time)
    return True

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, request: Request):
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # Check rate limiting for registration
    if not check_rate_limit(client_ip, "register", 3, 300):  # 3 registrations per 5 minutes
        logging_service.warning(request, f"Rate limit exceeded for registration from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        logging_service.warning(request, "Password does not meet strength requirements")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
        )
    
    try:
        logging_service.info(request, f"Registration attempt for email: {user_data.email}")
        
        # Check if user already exists
        existing_user = user_storage.get_user_by_email(user_data.email)
        if existing_user:
            if existing_user.get("verified", False):
                logging_service.warning(request, f"User {user_data.email} already registered and verified")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Email already registered"
                )
            else:
                # Resend verification for unverified users
                logging_service.info(request, f"User {user_data.email} exists but not verified. Resending verification.")
                token = create_token({"email": user_data.email, "type": "verification"}, 1440)  # 24 hours
                await send_verification_email(user_data.email, token)
                return {
                    "email": user_data.email, 
                    "verified": False, 
                    "is_logged_in": False, 
                    "message": "Verification email resent"
                }
        
        # Create new user
        logging_service.info(request, f"Creating new user: {user_data.email}")
        hashed_password = hash_password(user_data.password)
        new_user = {
            "email": user_data.email,
            "password": hashed_password,
            "full_name": user_data.full_name,
            "company_name": user_data.company_name,
            "company_address": user_data.company_address,
            "verified": False,
            "created_at": time.time(),
            "last_login": None
        }
        
        # Save user to storage
        save_result = user_storage.save_user(new_user)
        if not save_result:
            logging_service.error(request, f"Failed to save user data for {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user data"
            )
        
        # Generate verification token (24 hour expiration)
        token = create_token({"email": user_data.email, "type": "verification"}, 1440)
        
        # Send verification email
        email_sent = await send_verification_email(user_data.email, token)
        if not email_sent and settings.ENV != "development":
            logging_service.warning(request, f"Failed to send verification email to {user_data.email}")
            # In production, this might be a critical error
            # For now, we'll continue with registration but warn the user
        
        logging_service.success(request, f"New user registered successfully: {user_data.email}")
        
        return {
            "email": user_data.email, 
            "verified": False, 
            "is_logged_in": False,
            "full_name": user_data.full_name,
            "message": "Registration successful. Please check your email for verification."
        }
    except ValidationError as e:
        logging_service.error(request, f"Validation error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Capture and log the complete traceback
        logging_service.error(request, f"Error during registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.get("/verify", response_class=HTMLResponse)
async def verify(token: str = Query(...), request: Request = None):
    try:
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            if request:
                logging_service.warning(request, f"Token verification failed: {payload['error']}")
            logger.warning(f"Token verification failed: {payload['error']}")
            return HTMLResponse(f"<h1>Verification failed</h1><p>{payload['error']}</p>", status_code=400)
        
        # Verify token type
        if payload.get("type") != "verification":
            if request:
                logging_service.warning(request, f"Invalid token type: {payload.get('type')}")
            logger.warning(f"Invalid token type: {payload.get('type')}")
            return HTMLResponse("<h1>Invalid verification token</h1>", status_code=400)
            
        email = payload.get("email")
        if not email:
            if request:
                logging_service.warning(request, "Missing email in verification token")
            logger.warning("Missing email in verification token")
            return HTMLResponse("<h1>Invalid verification link</h1>", status_code=400)
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"User not found during verification: {email}")
            logger.warning(f"User not found during verification: {email}")
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Update user verification status
        user["verified"] = True
        user["verified_at"] = time.time()
        update_result = user_storage.update_user(user)
        
        if not update_result:
            if request:
                logging_service.error(request, f"Failed to update user verification status: {email}")
            logger.error(f"Failed to update user verification status: {email}")
            return HTMLResponse("<h1>Verification failed</h1><p>Failed to update user status.</p>", status_code=500)
        
        if request:
            logging_service.success(request, f"User verified: {email}")
        logger.info(f"User verified: {email}")
        
        return """
        <html>
            <head>
                <title>Email Verified</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
                    h1 { color: #28a745; }
                    p { margin: 20px 0; }
                    .btn { background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; }
                </style>
            </head>
            <body>
                <h1>Email Successfully Verified!</h1>
                <p>Your account has been verified. You can now log in to your account.</p>
                <a href="/" class="btn">Go to Login</a>
            </body>
        </html>
        """
    except Exception as e:
        if request:
            logging_service.error(request, f"Email verification error: {str(e)}")
        logger.error(f"Email verification error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse(f"<h1>Verification failed</h1><p>An error occurred during verification</p>", status_code=400)

@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin, request: Request):
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # Check rate limiting for login attempts
    if not check_rate_limit(client_ip, "login", 5, 300):  # 5 login attempts per 5 minutes
        logging_service.warning(request, f"Rate limit exceeded for login from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

    try:
        logging_service.info(request, f"Login attempt for: {user_data.email}")
        
        # Get user from storage
        user = user_storage.get_user_by_email(user_data.email)
        if not user:
            # Use same error message for security (don't reveal if email exists)
            logging_service.warning(request, f"Login failed - user not found: {user_data.email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        # Check if user is verified
        if not user.get("verified", False):
            logging_service.warning(request, f"Login failed - user not verified: {user_data.email}")
            # Create a more detailed message in the login response
            token = create_token({"email": user_data.email, "type": "verification"}, 1440)  # 24 hours
            await send_verification_email(user_data.email, token)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Email not verified. We've sent a new verification email to your address."
            )
        
        # Verify password
        if not verify_password(user_data.password, user["password"]):
            logging_service.warning(request, f"Login failed - invalid password for {user_data.email} from {client_ip}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        # Update last login timestamp
        user["last_login"] = time.time()
        update_result = user_storage.update_user(user)
        if not update_result:
            logging_service.error(request, f"Failed to update last login time for user: {user_data.email}")
        
        # Generate access token (default expiration)
        token = create_token({"sub": user_data.email})
        
        logging_service.success(request, f"User logged in successfully: {user_data.email}")
        
        return {
            "email": user_data.email,
            "verified": True,
            "is_logged_in": True,
            "full_name": user.get("full_name"),
            "message": "Login successful",
            "token": token
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging_service.error(request, f"Login error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

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
    
    In a production system, we could implement token revocation with a blacklist
    """
    if request:
        logging_service.info(request, "User logged out")
    return {"message": "Logged out successfully"}

# app/routes/auth.py - Add these new routes and modify existing ones

# New imports needed
from fastapi import BackgroundTasks
import uuid

# Add these routes to the auth.py file

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Send password reset link to user's email
    """
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # Check rate limiting for password reset requests
    if not check_rate_limit(client_ip, "forgot_password", 3, 300):  # 3 requests per 5 minutes
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
        
        # Send password reset email
        background_tasks.add_task(send_password_reset_email, email, reset_token)
        
        logging_service.success(request, f"Password reset email sent to: {email}")
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    except Exception as e:
        logging_service.error(request, f"Password reset error: {str(e)}")
        logger.error(traceback.format_exc())
        # Return generic message to avoid revealing if email exists
        return {"message": "If your email is registered, you will receive a password reset link"}

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(token: str = Query(...), request: Request = None):
    """
    Display password reset form for valid tokens
    """
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            if request:
                logging_service.warning(request, f"Password reset form - token error: {payload['error']}")
            return HTMLResponse(f"<h1>Password Reset Failed</h1><p>{payload['error']}</p>", status_code=400)
        
        # Verify token type
        if payload.get("type") != "password_reset":
            if request:
                logging_service.warning(request, f"Invalid token type for password reset: {payload.get('type')}")
            return HTMLResponse("<h1>Invalid password reset token</h1>", status_code=400)
        
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
        return f"""
        <html>
            <head>
                <title>Reset Password</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; }}
                    .form-group {{ margin-bottom: 15px; }}
                    label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                    input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
                    button {{ background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }}
                    .password-requirements {{ background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 0.9em; }}
                    .error {{ color: red; display: none; margin-top: 5px; }}
                </style>
            </head>
            <body>
                <h1>Reset Your Password</h1>
                <form id="resetForm" method="POST" action="/api/reset-password-confirm">
                    <input type="hidden" name="token" value="{token}">
                    <div class="form-group">
                        <label for="new_password">New Password</label>
                        <input type="password" id="new_password" name="new_password" required>
                        <div class="error" id="password-error">Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters</div>
                    </div>
                    <div class="form-group">
                        <label for="confirm_password">Confirm Password</label>
                        <input type="password" id="confirm_password" name="confirm_password" required>
                        <div class="error" id="confirm-error">Passwords do not match</div>
                    </div>
                    <div class="password-requirements">
                        Password must contain at least 8 characters including:
                        <ul>
                            <li>At least one uppercase letter</li>
                            <li>At least one lowercase letter</li>
                            <li>At least one number</li>
                            <li>At least one special character (!@#$%^&*...)</li>
                        </ul>
                    </div>
                    <button type="submit">Reset Password</button>
                </form>
                
                <script>
                    document.getElementById('resetForm').addEventListener('submit', function(e) {{
                        const password = document.getElementById('new_password').value;
                        const confirmPassword = document.getElementById('confirm_password').value;
                        let valid = true;
                        
                        // Reset errors
                        document.getElementById('password-error').style.display = 'none';
                        document.getElementById('confirm-error').style.display = 'none';
                        
                        // Check password strength
                        const hasUppercase = /[A-Z]/.test(password);
                        const hasLowercase = /[a-z]/.test(password);
                        const hasNumber = /[0-9]/.test(password);
                        const hasSpecial = /[!@#$%^&*(),.?":{{}}|<>]/.test(password);
                        
                        if (password.length < 8 || !hasUppercase || !hasLowercase || !hasNumber || !hasSpecial) {{
                            document.getElementById('password-error').style.display = 'block';
                            valid = false;
                        }}
                        
                        // Check password match
                        if (password !== confirmPassword) {{
                            document.getElementById('confirm-error').style.display = 'block';
                            valid = false;
                        }}
                        
                        if (!valid) {{
                            e.preventDefault();
                        }}
                    }});
                </script>
            </body>
        </html>
        """
    except Exception as e:
        if request:
            logging_service.error(request, f"Password reset form error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse("<h1>Error Displaying Password Reset Form</h1>", status_code=500)

@router.post("/reset-password-confirm", response_class=HTMLResponse)
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
        
        # Verify token
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            if request:
                logging_service.warning(request, f"Password reset confirm - token error: {payload['error']}")
            return HTMLResponse(f"<h1>Password Reset Failed</h1><p>{payload['error']}</p>", status_code=400)
        
        # Verify token type
        if payload.get("type") != "password_reset":
            if request:
                logging_service.warning(request, f"Invalid token type for password reset: {payload.get('type')}")
            return HTMLResponse("<h1>Invalid password reset token</h1>", status_code=400)
        
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
        
        # Check if new password is the same as old password
        if verify_password(new_password, user["password"]):
            if request:
                logging_service.warning(request, f"Password reset - new password same as old: {email}")
            return HTMLResponse("<h1>New password cannot be the same as current password</h1>", status_code=400)
        
        # Check if password history exists and add the current password to it
        if "password_history" not in user:
            user["password_history"] = []
        
        # Add current password to history if it's not already there
        if user["password"] not in user["password_history"]:
            user["password_history"].append(user["password"])
        
        # Limit password history to last 5 passwords
        user["password_history"] = user["password_history"][-5:]
        
        # Check if new password matches any password in history
        for old_password_hash in user["password_history"]:
            if verify_password(new_password, old_password_hash):
                if request:
                    logging_service.warning(request, f"Password reset - password found in history: {email}")
                return HTMLResponse("<h1>New password cannot be the same as any of your previous 5 passwords</h1>", status_code=400)
        
        # Update password
        user["password"] = hash_password(new_password)
        user["password_changed_at"] = time.time()
        update_result = user_storage.update_user(user)
        
        if not update_result:
            if request:
                logging_service.error(request, f"Failed to save new password for user: {email}")
            return HTMLResponse("<h1>Failed to update password</h1>", status_code=500)
        
        if request:
            logging_service.success(request, f"Password reset successful for user: {email}")
        
        return """
        <html>
            <head>
                <title>Password Reset Success</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
                    h1 { color: #28a745; }
                    p { margin: 20px 0; }
                    .btn { background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; }
                </style>
            </head>
            <body>
                <h1>Password Reset Successful!</h1>
                <p>Your password has been updated successfully.</p>
                <a href="/" class="btn">Go to Login</a>
            </body>
        </html>
        """
    except Exception as e:
        if request:
            logging_service.error(request, f"Password reset confirm error: {str(e)}")
        logger.error(traceback.format_exc())
        return HTMLResponse("<h1>Error Resetting Password</h1>", status_code=500)

# Add this to change-password route to implement password history checking
@router.post("/change-password")
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
        
        # Check if new password is the same as current password
        if verify_password(new_password, user["password"]):
            if request:
                logging_service.warning(request, f"Password change failed - new password same as current: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password cannot be the same as current password"
            )
        
        # Check if password history exists and add the current password to it
        if "password_history" not in user:
            user["password_history"] = []
        
        # Add current password to history if it's not already there
        if user["password"] not in user["password_history"]:
            user["password_history"].append(user["password"])
        
        # Limit password history to last 5 passwords
        user["password_history"] = user["password_history"][-5:]
        
        # Check if new password matches any password in history
        for old_password_hash in user["password_history"]:
            if verify_password(new_password, old_password_hash):
                if request:
                    logging_service.warning(request, f"Password change failed - password found in history: {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password cannot be the same as any of your previous 5 passwords"
                )
        
        # Update password
        user["password"] = hash_password(new_password)
        user["password_changed_at"] = time.time()
        update_result = user_storage.update_user(user)
        
        if not update_result:
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

# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Request, Response, Depends, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import time
import logging
from pydantic import ValidationError

# Use relative imports for better compatibility
from app.models.user_models import UserRegister, UserLogin, UserResponse
from app.services.storage import UserStorage
from app.services.crypto import encrypt_data, decrypt_data
from app.services.email_utils import send_verification_email
from app.services.utils import hash_password, verify_password, create_token, verify_token, validate_password_strength
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
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
        logger.warning(f"Rate limit exceeded for registration from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
        )
    
    try:
        # Check if user already exists
        existing_user = user_storage.get_user_by_email(user_data.email)
        if existing_user:
            if existing_user.get("verified", False):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Email already registered"
                )
            else:
                # Resend verification for unverified users
                token = create_token({"email": user_data.email, "type": "verification"}, 1440)  # 24 hours
                await send_verification_email(user_data.email, token)
                return {
                    "email": user_data.email, 
                    "verified": False, 
                    "is_logged_in": False, 
                    "message": "Verification email resent"
                }
        
        # Create new user
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
        user_storage.save_user(new_user)
        
        # Generate verification token (24 hour expiration)
        token = create_token({"email": user_data.email, "type": "verification"}, 1440)
        
        # Send verification email
        await send_verification_email(user_data.email, token)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return {
            "email": user_data.email, 
            "verified": False, 
            "is_logged_in": False,
            "full_name": user_data.full_name,
            "message": "Registration successful. Please check your email for verification."
        }
    except ValidationError as e:
        logger.error(f"Validation error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@router.get("/verify", response_class=HTMLResponse)
async def verify(token: str = Query(...)):
    try:
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            return HTMLResponse(f"<h1>Verification failed</h1><p>{payload['error']}</p>", status_code=400)
        
        # Verify token type
        if payload.get("type") != "verification":
            return HTMLResponse("<h1>Invalid verification token</h1>", status_code=400)
            
        email = payload.get("email")
        if not email:
            return HTMLResponse("<h1>Invalid verification link</h1>", status_code=400)
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Update user verification status
        user["verified"] = True
        user["verified_at"] = time.time()
        user_storage.update_user(user)
        
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
        logger.error(f"Email verification error: {e}")
        return HTMLResponse(f"<h1>Verification failed</h1><p>An error occurred during verification</p>", status_code=400)

@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin, request: Request):
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # Check rate limiting for login attempts
    if not check_rate_limit(client_ip, "login", 5, 300):  # 5 login attempts per 5 minutes
        logger.warning(f"Rate limit exceeded for login from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )

    try:
        # Get user from storage
        user = user_storage.get_user_by_email(user_data.email)
        if not user:
            # Use same error message for security (don't reveal if email exists)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        # Check if user is verified
        if not user.get("verified", False):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please verify your email before logging in")
        
        # Verify password
        if not verify_password(user_data.password, user["password"]):
            logger.warning(f"Failed login attempt for {user_data.email} from {client_ip}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
        # Update last login timestamp
        user["last_login"] = time.time()
        user_storage.update_user(user)
        
        # Generate access token (default expiration)
        token = create_token({"sub": user_data.email})
        
        logger.info(f"User logged in: {user_data.email}")
        
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
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.get("/status")
async def check_login_status(token: str = Query(None)):
    """
    Check if a user is logged in by validating their token
    """
    if not token:
        return {"is_logged_in": False}
    
    try:
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            return {"is_logged_in": False, "error": payload["error"]}
        
        email = payload.get("sub")
        if not email:
            return {"is_logged_in": False}
        
        user = user_storage.get_user_by_email(email)
        if not user or not user.get("verified", False):
            return {"is_logged_in": False}
        
        return {
            "is_logged_in": True,
            "email": email,
            "full_name": user.get("full_name")
        }
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return {"is_logged_in": False, "error": "Token verification failed"}

@router.post("/logout")
async def logout():
    """
    No server-side logout is needed for JWT tokens,
    but we provide this endpoint for front-end consistency
    
    In a production system, we could implement token revocation with a blacklist
    """
    return {"message": "Logged out successfully"}

@router.post("/change-password")
async def change_password(
    current_password: str, 
    new_password: str,
    token: str = Query(...),
):
    """
    Change user password with verification of current password
    """
    try:
        # Verify token
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        # Get user
        user = user_storage.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
            )
        
        # Update password
        user["password"] = hash_password(new_password)
        user["password_changed_at"] = time.time()
        user_storage.update_user(user)
        
        logger.info(f"Password changed for user: {email}")
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )
# Modified app/services/auth/authentication_forms.py
from fastapi import HTTPException, Request, status
from typing import Dict
import time
import logging
import traceback

from app.models.user_models import UserRegister, UserLogin, UserResponse
from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage  # Import the new company storage
from app.services.auth.email_utils import send_verification_email
from app.services.auth.utils import hash_password, verify_password, create_token, validate_password_strength, verify_token
from app.services.auth import logging_service
from app.services.auth.RateLimiter import rate_limiter
from app.services.auth.auth_templates import HTML_TEMPLATES
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
company_storage = CompanyStorage()  # Initialize company storage

# Token validation helper
def validate_token(token: str, token_type: str = None) -> Dict[str, str]:
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

# Route handlers - defined as regular functions (not decorated with router)
async def register(user_data: UserRegister, request: Request):
    """
    Handle user registration
    """
    # Rate limiting check
    client_ip = request.client.host
    if not rate_limiter.check_rate_limit(client_ip, "register", 3, 300):  # 3 registrations per 5 minutes
        logging_service.warning(request, f"Rate limit exceeded for registration from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Validate password strength
    if not validate_password_strength(user_data.password):
        logging_service.warning(request, f"Password does not meet strength requirements")
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
        
        # Check company registration restriction
        company_name = user_data.company_name
        if company_name:
            # Check if the company is already registered
            if company_storage.is_company_registered(company_name):
                # MODIFIED: Block regular registration for existing companies
                logging_service.warning(request, f"Unauthorized registration attempt for existing company {company_name} by {user_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This company is already registered. New users for this company must be added by an existing team member."
                )
        
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
            "last_login": None,
            "password_history": []  # Initialize empty password history
        }
        
        # Save user to storage
        save_result = user_storage.save_user(new_user)
        if not save_result:
            logging_service.error(request, f"Failed to save user data for {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user data"
            )
        
        # If company name is provided and company doesn't exist yet, register it
        if company_name and not company_storage.is_company_registered(company_name):
            company_storage.add_company(company_name, user_data.email)
            logging_service.info(request, f"Registered new company: {company_name} with admin: {user_data.email}")
        
        # Generate verification token (24 hour expiration)
        token = create_token({"email": user_data.email, "type": "verification"}, 1440)
        
        # Send verification email
        email_sent = await send_verification_email(user_data.email, token)
        if not email_sent and settings.ENV != "development":
            logging_service.warning(request, f"Failed to send verification email to {user_data.email}")
        
        logging_service.success(request, f"New user registered successfully: {user_data.email}")
        
        return {
            "email": user_data.email, 
            "verified": False, 
            "is_logged_in": False,
            "full_name": user_data.full_name,
            "message": "Registration successful. Please check your email for verification."
        }
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

async def verify(token: str, request: Request = None):
    """
    Handle email verification
    """
    try:
        # Use the validate_token function defined in this file
        try:
            payload = validate_token(token, "verification")
        except HTTPException as e:
            # Return the exception detail
            return {"success": False, "message": e.detail, "status_code": e.status_code}
        
        email = payload.get("email")
        if not email:
            if request:
                logging_service.warning(request, "Missing email in verification token")
            return {"success": False, "message": "Invalid verification link", "status_code": 400}
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            if request:
                logging_service.warning(request, f"User not found during verification: {email}")
            return {"success": False, "message": "User not found", "status_code": 404}
        
        # Update user verification status
        user["verified"] = True
        user["verified_at"] = time.time()
        update_result = user_storage.update_user(user)
        
        if not update_result:
            if request:
                logging_service.error(request, f"Failed to update user verification status: {email}")
            return {"success": False, "message": "Failed to update user status", "status_code": 500}
        
        if request:
            logging_service.success(request, f"User verified: {email}")
        logger.info(f"User verified: {email}")
        
        return {"success": True, "html": HTML_TEMPLATES["verification_success"]}
    except Exception as e:
        if request:
            logging_service.error(request, f"Email verification error: {str(e)}")
        logger.error(f"Email verification error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"success": False, "message": "An error occurred during verification", "status_code": 400}

async def login(user_data: UserLogin, request: Request):
    """
    Handle user login
    """
    # Rate limiting check
    client_ip = request.client.host
    if not rate_limiter.check_rate_limit(client_ip, "login", 5, 300):  # 5 login attempts per 5 minutes
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
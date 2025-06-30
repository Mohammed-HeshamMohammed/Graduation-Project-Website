# app/services/auth/authentication_forms.py
from fastapi import HTTPException, Request, status
from typing import Dict, Any
import time
import logging
import traceback
import uuid
from pathlib import Path
from app.models.user_models import UserRegister, UserLogin
from app.services.storage.user_storage import UserStorage
from app.services.email_utils import send_verification_email, send_welcome_email
from app.services.utils.auth_utils import AuthUtils
from app.services import logging_service
from app.services.auth.RateLimiter import rate_limiter
from app.config import settings
from app.services.password_handler.validators import validate_token, validate_password_strength
from app.services.password_handler.exceptions import PasswordValidationError
from app.services.password_handler.history_manager import update_user_password_with_history
from app.services.password_handler.reset_handler import (
    forgot_password,
    reset_password_form,
    reset_password_confirm
)
from app.services.password_handler.change_handler import change_password

logger = logging.getLogger(__name__)

class AuthForms:
    _user_storage = UserStorage()
    
    @staticmethod
    def _get_html_template(template_name: str, **kwargs) -> str:
        try:
            template_path = Path(__file__).parent.parent.parent / "templates" / "auth" / f"{template_name}.html"
            if not template_path.exists():
                template_path = Path("app/templates/auth") / f"{template_name}.html"
            
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                    
                for key, value in kwargs.items():
                    html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
                    
                return html_content
            else:
                logger.error(f"Template file not found: {template_path}")
                return f"<html><body><h1>Template Error</h1><p>Could not load {template_name} template</p></body></html>"
                
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return f"<html><body><h1>Template Error</h1><p>Error loading {template_name}: {str(e)}</p></body></html>"
    
    @staticmethod
    def _check_rate_limit(request: Request, endpoint: str, limit: int, window: int):
        client_ip = request.client.host
        if not rate_limiter.check_rate_limit(client_ip, endpoint, limit, window):
            logging_service.warning(request, f"Rate limit exceeded for {endpoint} from {client_ip}")
            logging_service.security_log(
                "RATE_LIMIT_EXCEEDED", 
                f"Rate limit exceeded for {endpoint}",
                request=request,
                module="auth",
                data={"client_ip": client_ip, "endpoint": endpoint, "limit": limit, "window": window}
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please try again later."
            )
    
    @staticmethod
    def _create_user_object(user_data: UserRegister) -> Dict[str, Any]:
        user_uuid = str(uuid.uuid4())
        company_id = str(uuid.uuid4())
        
        return {
            "uuid": user_uuid,
            "email": user_data.email,
            "password": AuthUtils.hash_password(user_data.password),
            "full_name": user_data.full_name,
            "company_name": user_data.company_name,
            "company_address": getattr(user_data, 'company_address', ''),
            "company_id": company_id,
            "verified": False,
            "is_logged_in": False,
            "privileges": ["owner"],
            "is_owner": True,
            "added_by": user_uuid,
            "added_by_email": user_data.email,
            "added_at": time.time(),
            "created_at": time.time(),
            "last_login": None,
            "password_history": []
        }
    
    @staticmethod
    def _create_response(user: Dict[str, Any], message: str, token: str = None) -> Dict[str, Any]:
        response = {
            "uuid": user.get("uuid"),
            "email": user["email"],
            "verified": user.get("verified", False),
            "is_logged_in": user.get("is_logged_in", False),
            "full_name": user.get("full_name"),
            "company_id": user.get("company_id"),
            "company_name": user.get("company_name"),
            "is_owner": user.get("is_owner", False),
            "message": message
        }
        if token:
            response["token"] = token
        return response
    
    @staticmethod
    def _log_security_event(event_type: str, message: str, request: Request, data: Dict = None):
        logging_service.security_log(event_type, message, request=request, module="auth", data=data or {})
    
    @staticmethod
    async def register(user_data: UserRegister, request: Request) -> Dict[str, Any]:
        AuthForms._check_rate_limit(request, "register", 3, 300)
        
        AuthForms._log_security_event(
            "REGISTRATION_ATTEMPT",
            f"User registration attempt for email: {user_data.email}",
            request,
            {"email": user_data.email, "company_name": user_data.company_name}
        )
        
        try:
            validate_password_strength(user_data.password)
        except PasswordValidationError as e:
            logging_service.warning(request, f"Password validation failed: {str(e)}")
            AuthForms._log_security_event(
                "WEAK_PASSWORD_ATTEMPT",
                f"Weak password used during registration for {user_data.email}",
                request,
                {"email": user_data.email, "validation_error": str(e)}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logging_service.warning(request, f"Password strength validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters and include uppercase, lowercase, numbers, and special characters"
            )
        
        try:
            logging_service.info(request, f"Registration attempt for email: {user_data.email}")
            
            existing_user = AuthForms._user_storage.get_user_by_email(user_data.email)
            if existing_user:
                if existing_user.get("verified", False):
                    logging_service.warning(request, f"User {user_data.email} already registered and verified")
                    AuthForms._log_security_event(
                        "DUPLICATE_REGISTRATION",
                        f"Attempt to register already verified email: {user_data.email}",
                        request,
                        {"email": user_data.email}
                    )
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
                else:
                    logging_service.info(request, f"User {user_data.email} exists but not verified. Resending verification.")
                    token = AuthUtils.create_token({"email": user_data.email, "type": "verification"}, 1440)
                    await send_verification_email(user_data.email, token)
                    AuthForms._log_security_event(
                        "VERIFICATION_RESENT",
                        f"Verification email resent for unverified user: {user_data.email}",
                        request,
                        {"email": user_data.email}
                    )
                    return AuthForms._create_response(existing_user, "Verification email resent")
            
            new_user = AuthForms._create_user_object(user_data)
            
            try:
                await update_user_password_with_history(
                    new_user, 
                    user_data.password, 
                    request, 
                    bypass_history_check=True
                )
                logging_service.info(request, f"Password history initialized for new user: {user_data.email}")
            except Exception as history_error:
                logging_service.warning(request, f"Failed to initialize password history for {user_data.email}: {str(history_error)}")
                logger.warning(f"Password history initialization failed for {user_data.email}: {history_error}")
            
            if not AuthForms._user_storage.save_user(new_user):
                logging_service.error(request, f"Failed to save user data for {user_data.email}")
                AuthForms._log_security_event(
                    "REGISTRATION_FAILURE",
                    f"Failed to save user data during registration: {user_data.email}",
                    request,
                    {"email": user_data.email, "error": "database_save_failed"}
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save user data"
                )
            
            token = AuthUtils.create_token({"email": user_data.email, "type": "verification"}, 1440)
            
            email_sent = await send_verification_email(user_data.email, token)
            if not email_sent and settings.ENV != "development":
                logging_service.warning(request, f"Failed to send verification email to {user_data.email}")
            
            AuthForms._log_security_event(
                "REGISTRATION_SUCCESS",
                f"New user registered successfully: {user_data.email}",
                request,
                {
                    "email": user_data.email,
                    "uuid": new_user["uuid"],
                    "company_name": user_data.company_name,
                    "verification_email_sent": email_sent
                }
            )
            
            logging_service.success(request, f"New user registered successfully: {user_data.email}")
            
            return AuthForms._create_response(new_user, "Registration successful. Please check your email for verification.")
            
        except HTTPException:
            raise
        except Exception as e:
            logging_service.error(request, f"Error during registration: {str(e)}")
            AuthForms._log_security_event(
                "REGISTRATION_EXCEPTION",
                f"Exception during registration for {user_data.email}: {str(e)}",
                request,
                {"email": user_data.email, "exception_type": type(e).__name__}
            )
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration"
            )
    
    @staticmethod
    async def verify(token: str, request: Request = None) -> Dict[str, Any]:
        if request:
            AuthForms._log_security_event(
                "EMAIL_VERIFICATION_ATTEMPT",
                "Email verification attempt initiated",
                request,
                {"token_provided": bool(token)}
            )
        
        try:
            payload = validate_token(token, "verification")
        except HTTPException as e:
            if request:
                AuthForms._log_security_event(
                    "INVALID_VERIFICATION_TOKEN",
                    "Invalid or expired verification token provided",
                    request,
                    {"error": e.detail, "status_code": e.status_code}
                )
            return {"success": False, "message": e.detail, "status_code": e.status_code}
        except Exception as e:
            if request:
                logging_service.warning(request, f"Token validation error: {str(e)}")
                AuthForms._log_security_event(
                    "VERIFICATION_TOKEN_ERROR",
                    f"Token validation error: {str(e)}",
                    request
                )
            return {"success": False, "message": "Invalid verification token", "status_code": 400}
        
        try:
            email = payload.get("email")
            if not email:
                if request:
                    logging_service.warning(request, "Missing email in verification token")
                    AuthForms._log_security_event(
                        "MALFORMED_VERIFICATION_TOKEN",
                        "Verification token missing email field",
                        request
                    )
                return {"success": False, "message": "Invalid verification link", "status_code": 400}
            
            user = AuthForms._user_storage.get_user_by_email(email)
            if not user:
                if request:
                    logging_service.warning(request, f"User not found during verification: {email}")
                    AuthForms._log_security_event(
                        "VERIFICATION_USER_NOT_FOUND",
                        f"Verification attempted for non-existent user: {email}",
                        request,
                        {"email": email}
                    )
                return {"success": False, "message": "User not found", "status_code": 404}
            
            if user.get("verified", False):
                if request:
                    AuthForms._log_security_event(
                        "DUPLICATE_VERIFICATION_ATTEMPT",
                        f"Verification attempted for already verified user: {email}",
                        request,
                        {"email": email, "uuid": user.get("uuid")}
                    )
            
            user["verified"] = True
            user["verified_at"] = time.time()
            
            if not AuthForms._user_storage.update_user(user):
                if request:
                    logging_service.error(request, f"Failed to update user verification status: {email}")
                    AuthForms._log_security_event(
                        "VERIFICATION_UPDATE_FAILED",
                        f"Failed to update verification status for user: {email}",
                        request,
                        {"email": email, "uuid": user.get("uuid")}
                    )
                return {"success": False, "message": "Failed to update user status", "status_code": 500}
            
            await send_welcome_email(email, user.get("full_name", ""))
            
            if request:
                AuthForms._log_security_event(
                    "EMAIL_VERIFICATION_SUCCESS",
                    f"User successfully verified email: {email}",
                    request,
                    {
                        "email": email,
                        "uuid": user.get("uuid"),
                        "full_name": user.get("full_name"),
                        "company_name": user.get("company_name"),
                        "verified_at": user["verified_at"]
                    }
                )
                logging_service.success(request, f"User verified: {email}")
            
            logger.info(f"User verified: {email}")
            
            html_content = AuthForms._get_html_template(
                "verification_success",
                user_name=user.get("full_name", ""),
                user_email=email,
                company_name=user.get("company_name", "")
            )
            return {"success": True, "html": html_content}
            
        except Exception as e:
            if request:
                logging_service.error(request, f"Email verification error: {str(e)}")
                AuthForms._log_security_event(
                    "EMAIL_VERIFICATION_EXCEPTION",
                    f"Exception during email verification: {str(e)}",
                    request,
                    {"exception_type": type(e).__name__}
                )
            logger.error(f"Email verification error: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "message": "An error occurred during verification", "status_code": 400}
    
    @staticmethod
    async def login(user_data: UserLogin, request: Request) -> Dict[str, Any]:
        AuthForms._check_rate_limit(request, "login", 5, 300)
        
        AuthForms._log_security_event(
            "LOGIN_ATTEMPT",
            f"Login attempt for email: {user_data.email}",
            request,
            {"email": user_data.email}
        )
        
        try:
            logging_service.info(request, f"Login attempt for: {user_data.email}")
            
            user = AuthForms._user_storage.get_user_by_email(user_data.email)
            if not user:
                logging_service.warning(request, f"Login failed - user not found: {user_data.email}")
                AuthForms._log_security_event(
                    "LOGIN_USER_NOT_FOUND",
                    f"Login attempted with non-existent email: {user_data.email}",
                    request,
                    {"email": user_data.email}
                )
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
            if not user.get("verified", False):
                logging_service.warning(request, f"Login failed - user not verified: {user_data.email}")
                AuthForms._log_security_event(
                    "LOGIN_UNVERIFIED_USER",
                    f"Login attempted with unverified email: {user_data.email}",
                    request,
                    {"email": user_data.email, "uuid": user.get("uuid")}
                )
                token = AuthUtils.create_token({"email": user_data.email, "type": "verification"}, 1440)
                await send_verification_email(user_data.email, token)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Email not verified. We've sent a new verification email to your address."
                )
            
            if not AuthUtils.verify_password(user_data.password, user["password"]):
                logging_service.warning(request, f"Login failed - invalid password for {user_data.email}")
                AuthForms._log_security_event(
                    "LOGIN_INVALID_PASSWORD",
                    f"Login failed with invalid password for: {user_data.email}",
                    request,
                    {"email": user_data.email, "uuid": user.get("uuid")}
                )
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
            user["last_login"] = time.time()
            user["is_logged_in"] = True
            
            if not AuthForms._user_storage.update_user(user):
                logging_service.error(request, f"Failed to update last login time for user: {user_data.email}")
            
            token = AuthUtils.create_token({"sub": user_data.email})
            
            AuthForms._log_security_event(
                "LOGIN_SUCCESS",
                f"User logged in successfully: {user_data.email}",
                request,
                {
                    "email": user_data.email,
                    "uuid": user.get("uuid"),
                    "full_name": user.get("full_name"),
                    "company_name": user.get("company_name"),
                    "last_login": user["last_login"],
                    "is_owner": user.get("is_owner", False)
                }
            )
            
            logging_service.success(request, f"User logged in successfully: {user_data.email}")
            
            return AuthForms._create_response(user, "Login successful", token)
            
        except HTTPException:
            raise
        except Exception as e:
            logging_service.error(request, f"Login error: {str(e)}")
            AuthForms._log_security_event(
                "LOGIN_EXCEPTION",
                f"Exception during login for {user_data.email}: {str(e)}",
                request,
                {"email": user_data.email, "exception_type": type(e).__name__}
            )
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login"
            )
    
    @staticmethod
    async def forgot_password(email: str, request: Request, background_tasks):
        AuthForms._log_security_event(
            "FORGOT_PASSWORD_ATTEMPT",
            f"Forgot password initiated for email: {email}",
            request,
            {"email": email}
        )
        
        try:
            result = await forgot_password(email, request, background_tasks)
            
            AuthForms._log_security_event(
                "FORGOT_PASSWORD_SUCCESS",
                f"Password reset email sent to: {email}",
                request,
                {"email": email}
            )
            
            return result
        except Exception as e:
            AuthForms._log_security_event(
                "FORGOT_PASSWORD_EXCEPTION",
                f"Exception during forgot password for {email}: {str(e)}",
                request,
                {"email": email, "exception_type": type(e).__name__}
            )
            raise
    
    @staticmethod
    async def reset_password_form(token: str, request: Request = None):
        if request:
            AuthForms._log_security_event(
                "RESET_PASSWORD_FORM_ACCESS",
                "Reset password form accessed",
                request,
                {"token_provided": bool(token)}
            )
        
        try:
            return await reset_password_form(token, request)
        except Exception as e:
            if request:
                AuthForms._log_security_event(
                    "RESET_PASSWORD_FORM_EXCEPTION",
                    f"Exception accessing reset password form: {str(e)}",
                    request,
                    {"exception_type": type(e).__name__}
                )
            raise
    
    @staticmethod
    async def reset_password_confirm(token: str, new_password: str, confirm_password: str, request: Request = None):
        if request:
            AuthForms._log_security_event(
                "PASSWORD_RESET_ATTEMPT",
                "Password reset confirmation initiated",
                request,
                {"token_provided": bool(token)}
            )
        
        try:
            result = await reset_password_confirm(token, new_password, confirm_password, request)
            
            if request and isinstance(result, dict) and result.get("success"):
                try:
                    payload = validate_token(token, "password_reset")
                    email = payload.get("email", "unknown")
                    AuthForms._log_security_event(
                        "PASSWORD_RESET_SUCCESS",
                        f"Password successfully reset for user: {email}",
                        request,
                        {"email": email}
                    )
                except:
                    AuthForms._log_security_event(
                        "PASSWORD_RESET_SUCCESS",
                        "Password reset completed successfully",
                        request
                    )
            
            return result
        except Exception as e:
            if request:
                AuthForms._log_security_event(
                    "PASSWORD_RESET_EXCEPTION",
                    f"Exception during password reset: {str(e)}",
                    request,
                    {"exception_type": type(e).__name__}
                )
            raise
    
    @staticmethod
    async def change_password(current_password: str, new_password: str, token: str, request: Request = None):
        if request:
            AuthForms._log_security_event(
                "PASSWORD_CHANGE_ATTEMPT",
                "Password change initiated",
                request,
                {"token_provided": bool(token)}
            )
        
        try:
            result = await change_password(current_password, new_password, token, request)
            
            if request and isinstance(result, dict) and result.get("success"):
                try:
                    payload = AuthUtils.verify_token(token)
                    email = payload.get("sub", "unknown")
                    AuthForms._log_security_event(
                        "PASSWORD_CHANGE_SUCCESS",
                        f"Password successfully changed for user: {email}",
                        request,
                        {"email": email}
                    )
                except:
                    AuthForms._log_security_event(
                        "PASSWORD_CHANGE_SUCCESS",
                        "Password change completed successfully",
                        request
                    )
            
            return result
        except Exception as e:
            if request:
                AuthForms._log_security_event(
                    "PASSWORD_CHANGE_EXCEPTION",
                    f"Exception during password change: {str(e)}",
                    request,
                    {"exception_type": type(e).__name__}
                )
            raise
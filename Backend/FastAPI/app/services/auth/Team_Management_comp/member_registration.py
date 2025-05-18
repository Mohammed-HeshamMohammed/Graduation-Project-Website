# app/services/auth/member_registration.py
import traceback
import time
import logging
from fastapi import HTTPException, Request, status

from app.models.user_models import TeamMemberRegister, UserRegister
from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage
from app.services.auth.user_privileges import UserPrivilege, can_add_members
from app.services.auth.email_utils import send_verification_email
from app.services.auth.utils import hash_password, create_token
from app.services.auth import logging_service

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
company_storage = CompanyStorage()

async def register_team_member(member_data: TeamMemberRegister, request: Request, current_user_email: str):
    """Register a team member under the same company as the current user"""
    try:
        logging_service.info(request, f"Team member registration attempt for: {member_data.email} by {current_user_email}")
        
        # Get current user
        current_user = user_storage.get_user_by_email(current_user_email)
        if not current_user:
            logging_service.error(request, f"Current user {current_user_email} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current user not found"
            )
        
        # Get company name from current user
        company_name = current_user.get("company_name")
        if not company_name:
            logging_service.error(request, f"Current user {current_user_email} has no company")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current user is not associated with a company"
            )
        
        # Check if current user is authorized to register team members using updated privileges
        user_privileges = company_storage.get_user_company_privileges(current_user_email, company_name)
        if not can_add_members(user_privileges):
            logging_service.warning(request, f"User {current_user_email} not authorized to add members to {company_name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to add team members for this company"
            )
        
        # Check if user already exists
        existing_user = user_storage.get_user_by_email(member_data.email)
        if existing_user:
            if existing_user.get("company_name") != company_name:
                logging_service.warning(request, f"User {member_data.email} already exists under a different company")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered under a different company"
                )
            elif existing_user.get("verified", False):
                logging_service.warning(request, f"User {member_data.email} already registered and verified")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Email already registered"
                )
            else:
                # Resend verification for unverified users
                logging_service.info(request, f"User {member_data.email} exists but not verified. Resending verification.")
                token = create_token({"email": member_data.email, "type": "verification"}, 1440)  # 24 hours
                await send_verification_email(member_data.email, token)
                return {
                    "email": member_data.email, 
                    "verified": False, 
                    "is_logged_in": False, 
                    "message": "Verification email resent"
                }
        
        # Register the new team member under the same company
        logging_service.info(request, f"Creating new team member: {member_data.email} under {company_name}")
        hashed_password = hash_password(member_data.password)
        new_user = {
            "email": member_data.email,
            "password": hashed_password,
            "full_name": member_data.full_name,
            "company_name": company_name,  # Use the company name from the current user
            "company_address": current_user.get("company_address"),
            "verified": False,
            "created_at": time.time(),
            "registered_by": current_user_email,  # Add information about who registered this user
            "last_login": None,
            "password_history": []
        }
        
        # Save user to storage
        save_result = user_storage.save_user(new_user)
        if not save_result:
            logging_service.error(request, f"Failed to save team member data for {member_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user data"
            )
        
        # Add the new user to the company with default MEMBER privilege
        company_storage.add_member(company_name, member_data.email, current_user_email)
        
        # Generate verification token (24 hour expiration)
        token = create_token({"email": member_data.email, "type": "verification"}, 1440)
        
        # Send verification email
        email_sent = await send_verification_email(member_data.email, token)
        
        logging_service.success(request, f"New team member registered successfully: {member_data.email}")
        
        return {
            "email": member_data.email, 
            "verified": False, 
            "is_logged_in": False,
            "full_name": member_data.full_name,
            "message": "Team member registration successful. Verification email sent."
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other exceptions
        logging_service.error(request, f"Error during team member registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during team member registration"
        )

async def register_company_owner(user_data: UserRegister, request: Request):
    """Register the first user for a company as the owner"""
    try:
        logging_service.info(request, f"Company owner registration attempt for: {user_data.email}")
        
        if not user_data.company_name:
            logging_service.error(request, "Company registration attempted without company name")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name is required for owner registration"
            )
        
        # Check if company already exists
        if company_storage.is_company_registered(user_data.company_name):
            logging_service.warning(request, f"Company {user_data.company_name} already registered")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company already registered"
            )
        
        # Check if user already exists
        existing_user = user_storage.get_user_by_email(user_data.email)
        if existing_user:
            logging_service.warning(request, f"User {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Register the user
        logging_service.info(request, f"Creating new company owner: {user_data.email} for company {user_data.company_name}")
        hashed_password = hash_password(user_data.password)
        new_user = {
            "email": user_data.email,
            "password": hashed_password,
            "full_name": user_data.full_name,
            "company_name": user_data.company_name,
            "company_address": user_data.company_address,
            "verified": False,
            "created_at": time.time(),
            "registered_by": None,  # Owner registers themselves
            "last_login": None,
            "password_history": []
        }
        
        # Save user to storage
        save_result = user_storage.save_user(new_user)
        if not save_result:
            logging_service.error(request, f"Failed to save owner data for {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user data"
            )
        
        # Register the company with this user as owner
        company_result = company_storage.add_company(user_data.company_name, user_data.email)
        if not company_result:
            logging_service.error(request, f"Failed to register company {user_data.company_name}")
            # Try to clean up the user if company registration fails
            user_storage.delete_user(user_data.email)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register company"
            )
        
        # Generate verification token (24 hour expiration)
        token = create_token({"email": user_data.email, "type": "verification"}, 1440)
        
        # Send verification email
        email_sent = await send_verification_email(user_data.email, token)
        
        logging_service.success(request, f"New company owner registered successfully: {user_data.email} for {user_data.company_name}")
        
        return {
            "email": user_data.email,
            "verified": False,
            "is_logged_in": False,
            "full_name": user_data.full_name,
            "company_name": user_data.company_name,
            "message": "Company registration successful. Verification email sent."
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other exceptions
        logging_service.error(request, f"Error during company owner registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during company registration"
        )
# app/services/auth/member_management.py
import traceback
import logging
from fastapi import HTTPException, Request, status
from typing import List

from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage
from app.services.auth.user_privileges import UserPrivilege, can_remove_members, can_manage_privileges, is_owner
from app.services.auth import logging_service

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
company_storage = CompanyStorage()

async def remove_team_member(email_to_remove: str, request: Request, current_user_email: str):
    """Remove a team member from the company"""
    try:
        logging_service.info(request, f"Team member removal attempt for: {email_to_remove} by {current_user_email}")
        
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
        
        # Check if current user is authorized to remove team members using updated privileges
        user_privileges = company_storage.get_user_company_privileges(current_user_email, company_name)
        if not can_remove_members(user_privileges):
            logging_service.warning(request, f"User {current_user_email} not authorized to remove members from {company_name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to remove team members from this company"
            )
        
        # Get privileges of user to be removed
        user_to_remove_privileges = company_storage.get_user_company_privileges(email_to_remove, company_name)
        
        # Prevent removing company owner
        if is_owner(user_to_remove_privileges):
            logging_service.warning(request, f"Attempt to remove owner {email_to_remove} from company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove the company owner"
            )
        
        # Check if user exists in the company
        if not company_storage.is_user_authorized_for_company(email_to_remove, company_name):
            logging_service.warning(request, f"User {email_to_remove} not found in company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in company"
            )
        
        # Remove user from company
        remove_result = company_storage.remove_member(company_name, email_to_remove, current_user_email)
        if not remove_result:
            logging_service.error(request, f"Failed to remove {email_to_remove} from company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove user from company"
            )
        
        logging_service.success(request, f"Team member {email_to_remove} removed successfully from company {company_name}")
        
        return {
            "email": email_to_remove,
            "message": "Team member removed successfully from company"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other exceptions
        logging_service.error(request, f"Error during team member removal: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during team member removal"
        )
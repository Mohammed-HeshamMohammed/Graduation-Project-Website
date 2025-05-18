# app/services/auth/privilege_management.py
import traceback
import logging
from fastapi import HTTPException, Request, status
from typing import List

from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage
from app.services.auth.user_privileges import UserPrivilege, can_manage_privileges, is_owner, get_dashboard_role
from app.services.auth import logging_service

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
company_storage = CompanyStorage()

async def update_member_privileges(email: str, privileges: List[str], request: Request, current_user_email: str):
    """Update a team member's privileges"""
    try:
        logging_service.info(request, f"Privilege update attempt for: {email} by {current_user_email}")
        
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
        
        # Check if current user is authorized to manage privileges using updated privileges
        user_privileges = company_storage.get_user_company_privileges(current_user_email, company_name)
        if not can_manage_privileges(user_privileges):
            logging_service.warning(request, f"User {current_user_email} not authorized to manage privileges in {company_name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to manage privileges in this company"
            )
        
        # Get privileges of user to be updated
        user_to_update_privileges = company_storage.get_user_company_privileges(email, company_name)
        
        # Prevent modifying owner's privileges by another user
        if is_owner(user_to_update_privileges) and current_user_email != email:
            logging_service.warning(request, f"Attempt to modify owner {email} privileges by {current_user_email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify the company owner's privileges"
            )
        
        # Check if user exists in the company
        if not company_storage.is_user_authorized_for_company(email, company_name):
            logging_service.warning(request, f"User {email} not found in company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in company"
            )
        
        # Validate all privileges are valid
        for privilege in privileges:
            if not UserPrivilege.is_valid_privilege(privilege):
                logging_service.warning(request, f"Invalid privilege provided: {privilege}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid privilege: {privilege}"
                )
        
        # Update user privileges
        update_result = company_storage.update_member_privileges(company_name, email, privileges, current_user_email)
        if not update_result:
            logging_service.error(request, f"Failed to update privileges for {email} in company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user privileges"
            )
        
        # Get the updated privileges to return
        updated_privileges = company_storage.get_user_company_privileges(email, company_name)
        
        # Get dashboard role based on updated privileges
        dashboard_role = get_dashboard_role(updated_privileges)
        
        logging_service.success(request, f"Privileges for {email} updated successfully in company {company_name}")
        
        return {
            "email": email,
            "privileges": updated_privileges,
            "dashboard_role": dashboard_role,
            "message": "User privileges updated successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other exceptions
        logging_service.error(request, f"Error during privilege update: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during privilege update"
        )
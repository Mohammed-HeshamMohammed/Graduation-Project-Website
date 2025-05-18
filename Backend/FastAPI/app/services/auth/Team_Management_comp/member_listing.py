# app/services/auth/member_listing.py
import traceback
import logging
from fastapi import HTTPException, Request, status

from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage
from app.services.auth.user_privileges import UserPrivilege, is_owner, get_dashboard_role
from app.services.auth import logging_service

# Configure logging
logger = logging.getLogger(__name__)

user_storage = UserStorage()
company_storage = CompanyStorage()

async def list_team_members(request: Request, current_user_email: str):
    """List all team members in the company with their privileges"""
    try:
        logging_service.info(request, f"Team members list requested by: {current_user_email}")
        
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
        
        # Check if current user is authorized for this company
        if not company_storage.is_user_authorized_for_company(current_user_email, company_name):
            logging_service.warning(request, f"User {current_user_email} not authorized for company {company_name}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view team members for this company"
            )
        
        # Get all members
        members_data = company_storage.get_company_members(company_name)
        
        # Format member information
        formatted_members = []
        for email, info in members_data.items():
            # Get user details from user storage
            user_details = user_storage.get_user_by_email(email) or {}
            
            # Get privileges and determine dashboard role
            privileges = info.get("privileges", [])
            dashboard_role = get_dashboard_role(privileges)
            
            member = {
                "email": email,
                "full_name": user_details.get("full_name", "Unknown"),
                "privileges": privileges,
                "dashboard_role": dashboard_role,
                "verified": user_details.get("verified", False),
                "added_by": info.get("added_by"),
                "added_at": info.get("added_at"),
                "is_owner": is_owner(privileges)
            }
            formatted_members.append(member)
        
        logging_service.success(request, f"Retrieved {len(formatted_members)} team members for company {company_name}")
        
        return {
            "total": len(formatted_members),
            "members": formatted_members
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log other exceptions
        logging_service.error(request, f"Error retrieving team members: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving team members"
        )
# app/services/auth/team_functions.py
from fastapi import APIRouter, HTTPException, Request, Query, status
from typing import Dict, Any, List
import logging
import traceback

from app.models.user_models import TeamMemberRegister, UserResponse, TeamMembersListResponse
from app.services.auth.utils import verify_token
from app.services.auth import logging_service
from app.services.auth.team_management import (
    register_team_member as tm_register_team_member,
    remove_team_member as tm_remove_team_member,
    update_member_privileges as tm_update_member_privileges,
    list_team_members as tm_list_team_members
)

# Configure logging
logger = logging.getLogger(__name__)

async def add_team_member(member_data: TeamMemberRegister, request: Request, token: str) -> UserResponse:
    """
    Register a new team member under the same company as the current authenticated user
    """
    try:
        # Verify token to get current user
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            logging_service.warning(request, f"Team member registration failed - token error: {payload['error']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        # Get current user email from token
        current_user_email = payload.get("sub")
        if not current_user_email:
            logging_service.warning(request, "Team member registration failed - no email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        # Call the team_management function to register the team member
        result = await tm_register_team_member(member_data, request, current_user_email)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging_service.error(request, f"Error during team member registration: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during team member registration"
        )

async def delete_team_member(email: str, request: Request, token: str) -> Dict[str, str]:
    """
    Remove a team member from the company
    """
    try:
        # Verify token to get current user
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            logging_service.warning(request, f"Team member removal failed - token error: {payload['error']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        # Get current user email from token
        current_user_email = payload.get("sub")
        if not current_user_email:
            logging_service.warning(request, "Team member removal failed - no email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        # Call the team_management function to remove the team member
        result = await tm_remove_team_member(email, request, current_user_email)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging_service.error(request, f"Error during team member removal: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during team member removal"
        )

async def modify_member_privileges(
    email: str, 
    privileges: List[str], 
    request: Request, 
    token: str
) -> Dict[str, Any]:
    """
    Update a team member's privileges
    """
    try:
        # Verify token to get current user
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            logging_service.warning(request, f"Privilege update failed - token error: {payload['error']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        # Get current user email from token
        current_user_email = payload.get("sub")
        if not current_user_email:
            logging_service.warning(request, "Privilege update failed - no email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        # Validate privileges against the known list
        from app.services.auth.user_privileges import UserPrivilege
        valid_privileges = [p for p in privileges if UserPrivilege.is_valid_privilege(p)]
        
        if not valid_privileges:
            logging_service.warning(request, f"No valid privileges provided: {privileges}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid privileges provided"
            )
        
        # Call the team_management function to update privileges
        result = await tm_update_member_privileges(email, valid_privileges, request, current_user_email)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging_service.error(request, f"Error during privilege update: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during privilege update"
        )

async def get_team_members(request: Request, token: str) -> TeamMembersListResponse:
    """
    List all team members under the same company as the authenticated user
    """
    try:
        # Verify token to get current user
        payload = verify_token(token)
        
        # Check for token errors
        if "error" in payload:
            logging_service.warning(request, f"List team members failed - token error: {payload['error']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"Authentication failed: {payload['error']}"
            )
        
        # Get current user email from token
        current_user_email = payload.get("sub")
        if not current_user_email:
            logging_service.warning(request, "List team members failed - no email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authentication token"
            )
        
        # Call the team_management function to list team members
        result = await tm_list_team_members(request, current_user_email)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging_service.error(request, f"Error listing team members: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while listing team members"
        )
# app/routes/auth.py
from fastapi import APIRouter, HTTPException, Request, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, List
import logging
import traceback
from fastapi import BackgroundTasks

# Use relative imports for better compatibility
from app.models.user_models import UserRegister, UserLogin, UserResponse, TeamMemberRegister, TeamMembersListResponse
from app.services.auth.storage import UserStorage
from app.services.auth.company_storage import CompanyStorage
from app.services.auth.email_utils import send_verification_email
from app.services.auth.utils import verify_token
from app.services.auth import logging_service
from app.services.auth.RateLimiter import rate_limiter
from app.services.auth.authentication_forms import register, verify, login
from app.services.auth.password_handler import (
    forgot_password, 
    reset_password_form, 
    reset_password_confirm, 
    change_password
)
# Import team functions from the dedicated module
from app.services.auth.team_functions import (
    add_team_member,
    delete_team_member,
    modify_member_privileges,
    get_team_members
)
# Import user status functions
from app.services.auth.user_status import check_login_status as get_login_status, perform_logout
# Import company management functions
from app.services.auth.company_management import (
    register_company,
    get_company_details,
    update_company_details,
    get_company_schema,
    add_company_location,
    update_company_location,
    remove_company_location,
    add_fleet_category,
    update_fleet_category,
    remove_fleet_category
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
user_storage = UserStorage()
company_storage = CompanyStorage()

# Register the imported route handlers
router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)(register)

# Fix for verify endpoint to properly handle HTML responses
@router.get("/verify", response_class=HTMLResponse)
async def verify_endpoint(token: str):
    """
    Verify a user's email address via token
    """
    result = await verify(token)
    if isinstance(result, str):
        return HTMLResponse(content=result)
    elif isinstance(result, dict) and "html" in result:
        return HTMLResponse(content=result["html"])
    else:
        # Handle error case
        error_html = f"<h1>Verification Error</h1><p>{result.get('message', 'Unknown error')}</p>"
        return HTMLResponse(content=error_html, status_code=result.get('status_code', 500))

router.post("/login", response_model=UserResponse)(login)

# Register password management route handlers
router.post("/forgot-password")(forgot_password)
router.get("/reset-password", response_class=HTMLResponse)(reset_password_form)
router.post("/reset-password-confirm", response_class=HTMLResponse)(reset_password_confirm)
router.post("/change-password")(change_password)

# Team management endpoints
@router.post("/team/register", response_model=UserResponse)
async def register_team_member(member_data: TeamMemberRegister, request: Request, token: str = Query(...)):
    """
    Register a new team member under the same company as the current authenticated user
    """
    return await add_team_member(member_data, request, token)

@router.delete("/team/members/{email}", response_model=Dict[str, str])
async def remove_team_member(email: str, request: Request, token: str = Query(...)):
    """
    Remove a team member from the company
    """
    return await delete_team_member(email, request, token)

@router.put("/team/members/{email}/privileges", response_model=Dict[str, Any])
async def update_member_privileges(
    email: str, 
    privileges: List[str], 
    request: Request, 
    token: str = Query(...)
):
    """
    Update a team member's privileges
    """
    return await modify_member_privileges(email, privileges, request, token)

@router.get("/team/members", response_model=TeamMembersListResponse)
async def list_team_members(request: Request, token: str = Query(...)):
    """
    List all team members under the same company as the authenticated user
    """
    return await get_team_members(request, token)

@router.get("/status")
async def check_login_status(token: str = Query(None), request: Request = None):
    """
    Check if a user is logged in by validating their token
    """
    return await get_login_status(token, request)

@router.post("/logout")
async def logout(request: Request = None):
    """
    No server-side logout is needed for JWT tokens,
    but we provide this endpoint for front-end consistency
    """
    return await perform_logout(request)

# Company management endpoints
@router.post("/company/register")
async def company_register_endpoint(
    company_name: str = Form(...), 
    request: Request = None, 
    token: str = Query(...)
):
    """
    Register a new company with the current user as owner
    """
    return await register_company(company_name, request, token)

@router.get("/company/details")
async def company_details_endpoint(company_name: str, token: str = Query(...)):
    """
    Get company details
    """
    return await get_company_details(company_name, token)

@router.put("/company/details")
async def update_company_details_endpoint(
    company_name: str = Form(...),
    company_details: Dict = Form(...),
    token: str = Query(...)
):
    """
    Update company details
    """
    return await update_company_details(company_name, company_details, token)

@router.get("/company/schema")
async def company_schema_endpoint(token: str = Query(...)):
    """
    Get company schema
    """
    return await get_company_schema(token)

# Company location management
@router.post("/company/locations")
async def add_location_endpoint(
    company_name: str = Form(...),
    location: Dict = Form(...),
    token: str = Query(...)
):
    """
    Add a location to a company
    """
    return await add_company_location(company_name, location, token)

@router.put("/company/locations/{location_index}")
async def update_location_endpoint(
    location_index: int,
    company_name: str = Form(...),
    location: Dict = Form(...),
    token: str = Query(...)
):
    """
    Update a company location
    """
    return await update_company_location(location_index, company_name, location, token)

@router.delete("/company/locations/{location_index}")
async def remove_location_endpoint(
    location_index: int,
    company_name: str = Form(...),
    token: str = Query(...)
):
    """
    Remove a company location
    """
    return await remove_company_location(location_index, company_name, token)

# Company fleet management
@router.post("/company/fleet-categories")
async def add_fleet_category_endpoint(
    company_name: str = Form(...),
    fleet_category: Dict = Form(...),
    token: str = Query(...)
):
    """
    Add a fleet category to a company
    """
    return await add_fleet_category(company_name, fleet_category, token)

@router.put("/company/fleet-categories/{category_index}")
async def update_fleet_category_endpoint(
    category_index: int,
    company_name: str = Form(...),
    fleet_category: Dict = Form(...),
    token: str = Query(...)
):
    """
    Update a fleet category
    """
    return await update_fleet_category(category_index, company_name, fleet_category, token)

@router.delete("/company/fleet-categories/{category_index}")
async def remove_fleet_category_endpoint(
    category_index: int,
    company_name: str = Form(...),
    token: str = Query(...)
):
    """
    Remove a fleet category
    """
    return await remove_fleet_category(category_index, company_name, token)
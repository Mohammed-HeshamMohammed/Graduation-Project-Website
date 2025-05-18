# app/services/auth/team_management.py
from fastapi import Request
from typing import List

from app.models.user_models import UserRegister, TeamMemberRegister
from app.services.auth.Team_Management_comp.member_registration import register_team_member as _register_team_member
from app.services.auth.Team_Management_comp.member_registration import register_company_owner as _register_company_owner
from app.services.auth.Team_Management_comp.member_management import remove_team_member as _remove_team_member
from app.services.auth.Team_Management_comp.privilege_management import update_member_privileges as _update_member_privileges
from app.services.auth.Team_Management_comp.member_listing import list_team_members as _list_team_members

# Re-export functions with the original signatures to maintain API compatibility

async def register_team_member(member_data: TeamMemberRegister, request: Request, current_user_email: str):
    """Register a team member under the same company as the current user"""
    return await _register_team_member(member_data, request, current_user_email)

async def remove_team_member(email_to_remove: str, request: Request, current_user_email: str):
    """Remove a team member from the company"""
    return await _remove_team_member(email_to_remove, request, current_user_email)

async def update_member_privileges(email: str, privileges: List[str], request: Request, current_user_email: str):
    """Update a team member's privileges"""
    return await _update_member_privileges(email, privileges, request, current_user_email)

async def list_team_members(request: Request, current_user_email: str):
    """List all team members in the company with their privileges"""
    return await _list_team_members(request, current_user_email)

async def register_company_owner(user_data: UserRegister, request: Request):
    """Register the first user for a company as the owner"""
    return await _register_company_owner(user_data, request)
# app/services/auth/company_management.py
from fastapi import APIRouter, HTTPException, Request, Depends, Query, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, List
import logging
import traceback

from app.services.auth.utils import verify_token
from app.services.auth.company_storage import CompanyStorage

# Configure logging
logger = logging.getLogger(__name__)
company_storage = CompanyStorage()

async def register_company(
    company_name: str, 
    request: Request = None, 
    token: str = None
):
    """
    Register a new company with the current user as owner
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        owner_email = payload["email"]
        
        # Check if company already exists
        if company_storage.is_company_registered(company_name):
            raise HTTPException(status_code=400, detail="Company already exists")
        
        # Register the company
        success = company_storage.add_company(company_name, owner_email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to register company")
        
        return {"status": "success", "message": f"Company {company_name} registered successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error registering company: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_company_details(company_name: str, token: str):
    """
    Get company details
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Check if user is authorized for this company
        if not company_storage.is_user_authorized_for_company(email, company_name):
            raise HTTPException(status_code=403, detail="Not authorized to access this company")
        
        # Get company details
        details = company_storage.get_company_details(company_name)
        if not details:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return details
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting company details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_company_details(
    company_name: str,
    company_details: Dict,
    token: str
):
    """
    Update company details
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Check if user has permissions to update company details
        if not company_storage.can_user_manage_privileges(email, company_name):
            raise HTTPException(status_code=403, detail="Not authorized to update company details")
        
        # Update company details
        success = company_storage.update_company_details(company_name, company_details, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update company details")
        
        return {"status": "success", "message": "Company details updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating company details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_company_schema(token: str):
    """
    Get company schema
    """
    try:
        # Verify token (simple auth check)
        payload = verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Get schema - this doesn't require company-specific permissions
        schema = company_storage.get_company_schema()
        return schema
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting company schema: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Company location management
async def add_company_location(
    company_name: str,
    location: Dict,
    token: str
):
    """
    Add a location to a company
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Add location
        success = company_storage.add_location(company_name, location, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add location")
        
        return {"status": "success", "message": "Location added successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding company location: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_company_location(
    location_index: int,
    company_name: str,
    location: Dict,
    token: str
):
    """
    Update a company location
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Update location
        success = company_storage.update_location(company_name, location_index, location, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update location")
        
        return {"status": "success", "message": "Location updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating company location: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def remove_company_location(
    location_index: int,
    company_name: str,
    token: str
):
    """
    Remove a company location
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Remove location
        success = company_storage.remove_location(company_name, location_index, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove location")
        
        return {"status": "success", "message": "Location removed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error removing company location: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Company fleet management
async def add_fleet_category(
    company_name: str,
    fleet_category: Dict,
    token: str
):
    """
    Add a fleet category to a company
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Add fleet category
        success = company_storage.add_fleet_category(company_name, fleet_category, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add fleet category")
        
        return {"status": "success", "message": "Fleet category added successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding fleet category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def update_fleet_category(
    category_index: int,
    company_name: str,
    fleet_category: Dict,
    token: str
):
    """
    Update a fleet category
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Update fleet category
        success = company_storage.update_fleet_category(company_name, category_index, fleet_category, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update fleet category")
        
        return {"status": "success", "message": "Fleet category updated successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating fleet category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def remove_fleet_category(
    category_index: int,
    company_name: str,
    token: str
):
    """
    Remove a fleet category
    """
    try:
        # Verify token and get user email
        payload = verify_token(token)
        if not payload or "email" not in payload:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        email = payload["email"]
        
        # Remove fleet category
        success = company_storage.remove_fleet_category(company_name, category_index, email)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove fleet category")
        
        return {"status": "success", "message": "Fleet category removed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error removing fleet category: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
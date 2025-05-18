# app/main.py
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime  # Import datetime module

import uvicorn
import sys
import os

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import auth, fleet
from app.config import settings
from app.middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware
from app.services.auth.logging_service import LoggingMiddleware  # Import LoggingMiddleware

# Define base directory
BASE_DIR = Path(__file__).resolve().parent

# Setup templates and static files directories
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(LoggingMiddleware)  # Add LoggingMiddleware

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Include authentication routes
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

# Include fleet management routes
app.include_router(fleet.router, prefix="/api/fleet", tags=["Fleet Management"])

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    # Group endpoints logically for better organization
    auth_endpoints = [
        # User Authentication
        {"group": "User Authentication", "endpoints": [
            {"method": "POST", "path": "/api/register", "desc": "Register a new user with email, password, full name, company name and address"},
            {"method": "GET", "path": "/api/verify", "desc": "Verify email using token from email link"},
            {"method": "POST", "path": "/api/login", "desc": "Login with email and password (only works after verification)"},
            {"method": "GET", "path": "/api/status", "desc": "Check if a user is currently logged in (using their token)"},
            {"method": "POST", "path": "/api/logout", "desc": "Logout a user (frontend will need to delete the token)"}
        ]},
        
        # Password Management
        {"group": "Password Management", "endpoints": [
            {"method": "POST", "path": "/api/change-password", "desc": "Change the user's password (requires current password and authentication)"},
            {"method": "POST", "path": "/api/forgot-password", "desc": "Request a password reset link to be sent to your email"},
            {"method": "GET", "path": "/api/reset-password", "desc": "Form to reset password (accessed via email link with token)"},
            {"method": "POST", "path": "/api/reset-password-confirm", "desc": "Process the password reset request with new password"}
        ]},
        
        # Team Management
        {"group": "Team Management", "endpoints": [
            {"method": "POST", "path": "/api/team/register", "desc": "Register a new team member under the same company as the authenticated user"},
            {"method": "GET", "path": "/api/team/members", "desc": "List all team members under the same company as the authenticated user"},
            {"method": "DELETE", "path": "/api/team/members/{email}", "desc": "Remove a team member from the company"},
            {"method": "PUT", "path": "/api/team/members/{email}/privileges", "desc": "Update a team member's privileges"}
        ]},
        
        # Company Management
        {"group": "Company Management", "endpoints": [
            {"method": "POST", "path": "/api/company/register", "desc": "Register a new company with the current user as owner"},
            {"method": "GET", "path": "/api/company/details", "desc": "Get company details"},
            {"method": "PUT", "path": "/api/company/details", "desc": "Update company details"},
            {"method": "GET", "path": "/api/company/schema", "desc": "Get company schema"}
        ]},
        
        # Company Locations
        {"group": "Company Locations", "endpoints": [
            {"method": "POST", "path": "/api/company/locations", "desc": "Add a location to a company"},
            {"method": "PUT", "path": "/api/company/locations/{location_index}", "desc": "Update a company location"},
            {"method": "DELETE", "path": "/api/company/locations/{location_index}", "desc": "Remove a company location"}
        ]},
        
        # Fleet Categories
        {"group": "Fleet Categories", "endpoints": [
            {"method": "POST", "path": "/api/company/fleet-categories", "desc": "Add a fleet category to a company"},
            {"method": "PUT", "path": "/api/company/fleet-categories/{category_index}", "desc": "Update a fleet category"},
            {"method": "DELETE", "path": "/api/company/fleet-categories/{category_index}", "desc": "Remove a fleet category"}
        ]}
    ]
    
    fleet_endpoints = [
        # Vehicle Management
        {"group": "Vehicle Management", "endpoints": [
            {"method": "POST", "path": "/api/fleet/vehicles", "desc": "Create a new vehicle"},
            {"method": "GET", "path": "/api/fleet/vehicles", "desc": "Get all vehicles for the logged-in user"},
            {"method": "GET", "path": "/api/fleet/vehicles/{vehicle_id}", "desc": "Get a specific vehicle by ID"},
            {"method": "PUT", "path": "/api/fleet/vehicles/{vehicle_id}", "desc": "Update an existing vehicle"},
            {"method": "DELETE", "path": "/api/fleet/vehicles/{vehicle_id}", "desc": "Delete a vehicle"}
        ]},
        
        # Driver Management
        {"group": "Driver Management", "endpoints": [
            {"method": "POST", "path": "/api/fleet/drivers", "desc": "Create a new driver"},
            {"method": "GET", "path": "/api/fleet/drivers", "desc": "Get all drivers for the logged-in user"},
            {"method": "GET", "path": "/api/fleet/drivers/{driver_id}", "desc": "Get a specific driver by ID"},
            {"method": "PUT", "path": "/api/fleet/drivers/{driver_id}", "desc": "Update an existing driver"},
            {"method": "DELETE", "path": "/api/fleet/drivers/{driver_id}", "desc": "Delete a driver"}
        ]}
    ]
    
    # Add current datetime to the template context
    now = datetime.now()
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "auth_endpoints": auth_endpoints,
            "fleet_endpoints": fleet_endpoints,
            "now": now  # Pass the datetime object to the template
        }
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
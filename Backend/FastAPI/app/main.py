# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import sys
import os

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import auth, fleet
from app.config import settings
from app.middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

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
def root():
    return """
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Authentication API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f2f4f8;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 40px;
                min-height: 100vh;
            }
            .container {
                background: #fff;
                padding: 30px 40px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
                max-width: 700px;
                width: 100%;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            p.description {
                text-align: center;
                color: #555;
                margin-bottom: 30px;
            }
            .endpoint {
                background: #f9fafc;
                padding: 15px 20px;
                border-left: 5px solid #3498db;
                margin: 15px 0;
                border-radius: 6px;
            }
            .endpoint strong {
                display: block;
                font-size: 15px;
                color: #2d3436;
                margin-bottom: 6px;
            }
            .endpoint p {
                margin: 0;
                font-size: 14px;
                color: #555;
            }
            code {
                background: #e8eef3;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Secure Authentication API</h1>
            <p class="description">Available endpoints for user and fleet management</p>

            <div class="endpoint">
                <strong>POST <code>/api/register</code></strong>
                <p>Register a new user with email, password, full name, company name and address</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/verify</code></strong>
                <p>Verify email using token from email link</p>
            </div>
            <div class="endpoint">
                <strong>POST <code>/api/login</code></strong>
                <p>Login with email and password (only works after verification)</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/status</code></strong>
                <p>Check if a user is currently logged in (using their token)</p>
            </div>
            <div class="endpoint">
                <strong>POST <code>/api/logout</code></strong>
                <p>Logout a user (frontend will need to delete the token)</p>
            </div>
            <div class="endpoint">
                <strong>POST <code>/api/change-password</code></strong>
                <p>Change the user's password (requires current password and authentication)</p>
            </div>

            <div class="endpoint">
                <strong>POST <code>/api/fleet/vehicles</code></strong>
                <p>Create a new vehicle</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/fleet/vehicles</code></strong>
                <p>Get all vehicles for the logged-in user</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/fleet/vehicles/{vehicle_id}</code></strong>
                <p>Get a specific vehicle by ID</p>
            </div>
            <div class="endpoint">
                <strong>PUT <code>/api/fleet/vehicles/{vehicle_id}</code></strong>
                <p>Update an existing vehicle</p>
            </div>
            <div class="endpoint">
                <strong>DELETE <code>/api/fleet/vehicles/{vehicle_id}</code></strong>
                <p>Delete a vehicle</p>
            </div>

            <div class="endpoint">
                <strong>POST <code>/api/fleet/drivers</code></strong>
                <p>Create a new driver</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/fleet/drivers</code></strong>
                <p>Get all drivers for the logged-in user</p>
            </div>
            <div class="endpoint">
                <strong>GET <code>/api/fleet/drivers/{driver_id}</code></strong>
                <p>Get a specific driver by ID</p>
            </div>
            <div class="endpoint">
                <strong>PUT <code>/api/fleet/drivers/{driver_id}</code></strong>
                <p>Update an existing driver</p>
            </div>
            <div class="endpoint">
                <strong>DELETE <code>/api/fleet/drivers/{driver_id}</code></strong>
                <p>Delete a driver</p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
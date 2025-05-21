# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import sys
import os

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import auth
from app.config import settings
from app.middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware
from app.services.logging_service import LoggingMiddleware  # Import LoggingMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

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

@app.get("/", response_class=HTMLResponse)
def root():
    return """
<html lang="en">
<body>
    <div class="container content">
        <div class="card">
            <div class="card-header">
                <div class="icon auth-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                </div>
                <h2>Authentication Endpoints</h2>
            </div>
            <div class="card-body">
                <div class="endpoints">
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/register</code>
                        </div>
                        <p class="endpoint-desc">Register a new user with email, password, full name, company name and address</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method get">GET</span>
                            <code class="endpoint-path">/api/verify</code>
                        </div>
                        <p class="endpoint-desc">Verify email using token from email link</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/login</code>
                        </div>
                        <p class="endpoint-desc">Login with email and password (only works after verification)</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method get">GET</span>
                            <code class="endpoint-path">/api/status</code>
                        </div>
                        <p class="endpoint-desc">Check if a user is currently logged in (using their token)</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/logout</code>
                        </div>
                        <p class="endpoint-desc">Logout a user (frontend will need to delete the token)</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/change-password</code>
                        </div>
                        <p class="endpoint-desc">Change the user's password (requires current password and authentication)</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/forgot-password</code>
                        </div>
                        <p class="endpoint-desc">Request a password reset link to be sent to your email</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method get">GET</span>
                            <code class="endpoint-path">/api/reset-password</code>
                        </div>
                        <p class="endpoint-desc">Form to reset password (accessed via email link with token)</p>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-header">
                            <span class="http-method post">POST</span>
                            <code class="endpoint-path">/api/reset-password-confirm</code>
                        </div>
                        <p class="endpoint-desc">Process the password reset request with new password</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
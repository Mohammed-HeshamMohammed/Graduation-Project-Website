from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from app.routes import auth
from app.config import settings

app = FastAPI(title="Secure Authentication API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Authentication API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
                code { background: #e9e9e9; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Secure Authentication API</h1>
            <p>Available endpoints:</p>
            <div class="endpoint">
                <strong>POST /api/register</strong>
                <p>Register a new user with email and password</p>
            </div>
            <div class="endpoint">
                <strong>GET /api/verify</strong>
                <p>Verify email using token from email link</p>
            </div>
            <div class="endpoint">
                <strong>POST /api/login</strong>
                <p>Login with email and password (only works after verification)</p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
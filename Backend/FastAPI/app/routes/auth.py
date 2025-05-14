from fastapi import APIRouter, HTTPException, Request, Response, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from app.models.user_models import UserRegister, UserLogin, UserResponse
from app.services.storage import UserStorage
from app.services.crypto import encrypt_data, decrypt_data
from app.services.email_utils import send_verification_email
from app.services.utils import hash_password, verify_password, create_token, verify_token

router = APIRouter()
user_storage = UserStorage()

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    # Check if user already exists
    existing_user = user_storage.get_user_by_email(user_data.email)
    if existing_user:
        if existing_user.get("verified", False):
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            # Resend verification for unverified users
            token = create_token({"email": user_data.email})
            await send_verification_email(user_data.email, token)
            return {"email": user_data.email, "verified": False, "message": "Verification email resent"}
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = {
        "email": user_data.email,
        "password": hashed_password,
        "verified": False
    }
    
    # Save user to storage
    user_storage.save_user(new_user)
    
    # Generate verification token
    token = create_token({"email": user_data.email})
    
    # Send verification email
    await send_verification_email(user_data.email, token)
    
    return {"email": user_data.email, "verified": False, "message": "Registration successful. Please check your email for verification."}

@router.get("/verify", response_class=HTMLResponse)
async def verify(token: str = Query(...)):
    try:
        payload = verify_token(token)
        email = payload.get("email")
        if not email:
            return HTMLResponse("<h1>Invalid verification link</h1>", status_code=400)
        
        # Get user from storage
        user = user_storage.get_user_by_email(email)
        if not user:
            return HTMLResponse("<h1>User not found</h1>", status_code=404)
        
        # Update user verification status
        user["verified"] = True
        user_storage.update_user(user)
        
        return """
        <html>
            <head>
                <title>Email Verified</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; }
                    h1 { color: #28a745; }
                    p { margin: 20px 0; }
                    .btn { background: #007bff; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Email Successfully Verified!</h1>
                <p>Your account has been verified. You can now log in to your account.</p>
                <a href="/" class="btn">Go to Login</a>
            </body>
        </html>
        """
    except Exception as e:
        return HTMLResponse(f"<h1>Verification failed</h1><p>{str(e)}</p>", status_code=400)

@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin):
    # Get user from storage
    user = user_storage.get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user is verified
    if not user.get("verified", False):
        raise HTTPException(status_code=401, detail="Please verify your email before logging in")
    
    # Verify password
    if not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate access token
    token = create_token({"sub": user_data.email})
    
    return {
        "email": user_data.email,
        "verified": True,
        "message": "Login successful",
        "token": token
    }


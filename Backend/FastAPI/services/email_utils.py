# app/main.py
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


# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # API settings
    API_TITLE = "Secure Authentication API"
    API_VERSION = "1.0.0"
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day
    TOKEN_ALGORITHM = "HS256"
    
    # Encryption settings
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "32-byte-key-for-AES-encryption!!!")
    
    # Storage settings
    DATA_DIR = os.getenv("DATA_DIR", "app/data")
    USER_DATA_FILE = os.getenv("USER_DATA_FILE", ".u94ks_userdata.bin")
    
    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")
    VERIFICATION_URL = os.getenv("VERIFICATION_URL", "http://localhost:8000/api/verify")

# Create singleton settings instance
settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)


# app/routes/auth.py
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


# app/models/user_models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    verified: bool
    message: str
    token: Optional[str] = None


# app/services/crypto.py
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import settings

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypts data using AES-256 encryption
    """
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    # Ensure key is exactly 32 bytes (256 bits)
    key = key[:32].ljust(32, b'\0')
    
    iv = os.urandom(16)  # Generate random initialization vector
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Pad the data to be a multiple of block size
    padded_data = pad(data, AES.block_size)
    
    # Encrypt the data
    encrypted_data = cipher.encrypt(padded_data)
    
    # Return IV + encrypted data
    return iv + encrypted_data

def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    Decrypts AES-256 encrypted data
    """
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    # Ensure key is exactly 32 bytes (256 bits)
    key = key[:32].ljust(32, b'\0')
    
    # Extract IV from the first 16 bytes
    iv = encrypted_data[:16]
    actual_data = encrypted_data[16:]
    
    # Create cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt and unpad
    decrypted_data = unpad(cipher.decrypt(actual_data), AES.block_size)
    
    return decrypted_data


# app/services/email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

async def send_verification_email(email: str, token: str):
    """
    Sends an email with a verification link
    """
    # Create verification URL with token
    verification_url = f"{settings.VERIFICATION_URL}?token={token}"
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your Email Address"
    message["From"] = settings.EMAIL_FROM
    message["To"] = email
    
    # Create both plain text and HTML versions
    text_content = f"""
    Please verify your email address by clicking the link below:
    
    {verification_url}
    
    If you did not register for this account, please ignore this email.
    """
    
    html_content = f"""
    <html>
      <body>
        <h2>Email Verification</h2>
        <p>Please verify your email address by clicking the button below:</p>
        <p>
          <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Verify Email
          </a>
        </p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{verification_url}</p>
        <p>If you did not register for this account, please ignore this email.</p>
      </body>
    </html>
    """
    
    # Attach parts
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")
    message.attach(part1)
    message.attach(part2)
    
    # For local development, just print the verification URL
    print(f"\n--- VERIFICATION EMAIL ---\nTo: {email}\nURL: {verification_url}\n--- END EMAIL ---\n")
    
    # Uncomment to actually send emails (requires valid SMTP credentials)
    """
    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email, message.as_string())
            return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    """
    
    # For development, we'll just return success
    return True


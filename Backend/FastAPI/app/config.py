# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
import secrets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # Application settings
    APP_NAME = "Secure Authentication API"
    API_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENV = os.getenv("ENV", "development")
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY and ENV == "development":
        # Generate a secure random key for development
        SECRET_KEY = secrets.token_urlsafe(32)
        logger.warning("No SECRET_KEY set! Generated a random secret key for development.")
    elif not SECRET_KEY:
        # In production, SECRET_KEY must be set
        raise ValueError("SECRET_KEY environment variable not set!")
    
    TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours default
    TOKEN_ALGORITHM = "HS256"
    
    # Encryption settings
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
    if not ENCRYPTION_KEY and ENV == "development":
        # Generate a secure random key for development
        ENCRYPTION_KEY = secrets.token_urlsafe(32)
        logger.warning("No ENCRYPTION_KEY set! Generated a random encryption key for development.")
    elif not ENCRYPTION_KEY:
        # In production, ENCRYPTION_KEY must be set
        raise ValueError("ENCRYPTION_KEY environment variable not set!")
    
    # Storage settings
    DATA_DIR = os.getenv("DATA_DIR", "app/data")
    USER_DATA_FILE = os.getenv("USER_DATA_FILE", "userdata.enc")
    
    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")
    VERIFICATION_URL = os.getenv("VERIFICATION_URL", "http://localhost:8000/api/verify")
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;"
    }
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["*"]
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("true", "1", "t")

# Create singleton settings instance
settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)
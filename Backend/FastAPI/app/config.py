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

# app/services/utils.py
import jwt
import bcrypt
from datetime import datetime, timedelta
import secrets
import string
from ..config import settings
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with proper cost factor
    """
    # Generate a salt with higher cost factor (12) than the default
    # Higher values are more secure but slower
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_token(data: dict, expires_minutes: int = None) -> str:
    """
    Create a JWT token with expiration
    """
    to_encode = data.copy()
    
    # Use provided expiration or default from settings
    if expires_minutes is None:
        expires_minutes = settings.TOKEN_EXPIRE_MINUTES
        
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    # Add token ID (jti) for potential revocation
    to_encode.update({"jti": generate_token_id()})
    
    # Create JWT token
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.TOKEN_ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise

def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.TOKEN_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return {"error": "Token expired"}
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return {"error": "Invalid token"}
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return {"error": "Token verification failed"}

def generate_token_id() -> str:
    """
    Generate a unique ID for JWT tokens
    """
    return secrets.token_hex(16)

def generate_verification_token() -> str:
    """
    Generate a secure token for email verification
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(64))

def validate_password_strength(password: str) -> bool:
    """
    Validates password strength
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    
    # Check for uppercase, lowercase, digit, and special character
    patterns = [
        r'[A-Z]',  # Uppercase
        r'[a-z]',  # Lowercase
        r'[0-9]',  # Digit
        r'[!@#$%^&*(),.?":{}|<>]'  # Special characters
    ]
    
    return all(re.search(pattern, password) for pattern in patterns)
import jwt
import bcrypt
from datetime import datetime, timedelta
from app.config import settings

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    # Generate a salt and hash the password
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_token(data: dict) -> str:
    """
    Create a JWT token with expiration
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt

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
    except jwt.PyJWTError:
        return {}
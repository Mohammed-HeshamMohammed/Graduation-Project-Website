# app/services/utils/auth_utils.py
import logging
from typing import Dict, Any
from jose import jwt
import bcrypt
from datetime import datetime, timedelta
import secrets
import string
from app.config import settings
import re

logger = logging.getLogger(__name__)

class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        try:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False

    @staticmethod
    def create_token(data: dict, expires_minutes: int = None) -> str:
        try:
            to_encode = data.copy()
            if expires_minutes is None:
                expires_minutes = settings.TOKEN_EXPIRE_MINUTES
            expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
            to_encode.update({
                "exp": expire, 
                "iat": datetime.utcnow(), 
                "jti": secrets.token_hex(16)
            })
            return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM)
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return {"error": "Token expired"}
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return {"error": "Invalid token"}
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return {"error": "Token verification failed"}

    @staticmethod
    def generate_verification_token() -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    @staticmethod
    def validate_password_strength(password: str) -> bool:
        try:
            if len(password) < 8:
                return False
            patterns = [r'[A-Z]', r'[a-z]', r'[0-9]', r'[!@#$%^&*(),.?":{}|<>]']
            return all(re.search(pattern, password) for pattern in patterns)
        except Exception as e:
            logger.error(f"Password validation failed: {e}")
            return False
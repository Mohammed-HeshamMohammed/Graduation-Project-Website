# app/models/user_models.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    full_name: str
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for uppercase, lowercase, digit, and special character
        patterns = [
            r'[A-Z]',  # Uppercase
            r'[a-z]',  # Lowercase
            r'[0-9]',  # Digit
            r'[!@#$%^&*(),.?":{}|<>]'  # Special characters
        ]
        
        if not all(re.search(pattern, v) for pattern in patterns):
            raise ValueError("Password must include uppercase, lowercase, numbers, and special characters")
        
        return v
    
    @validator('full_name')
    def full_name_not_empty(cls, v):
        """Validate that full name is not empty"""
        if not v or v.strip() == "":
            raise ValueError("Full name cannot be empty")
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    verified: bool
    message: str
    is_logged_in: bool = False
    token: Optional[str] = None
    full_name: Optional[str] = None
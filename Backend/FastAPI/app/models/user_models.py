# app/services/auth/user_models.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    """Model for user registration with company info"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    company_name: str
    company_address: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Model for user response data"""
    email: str
    verified: bool
    is_logged_in: bool
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    message: Optional[str] = None
    token: Optional[str] = None

class TeamMemberRegister(BaseModel):
    """Model for registering a team member"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class TeamMember(BaseModel):
    """Model for team member data"""
    email: str
    full_name: str
    privileges: List[str]
    verified: bool
    added_by: Optional[str] = None
    added_at: Optional[float] = None
    is_owner: bool = False

class TeamMembersListResponse(BaseModel):
    """Model for response when listing team members"""
    total: int
    members: List[Dict[str, Any]]

class PrivilegeUpdate(BaseModel):
    """Model for updating user privileges"""
    privileges: List[str]
"""
Authentication schemas for API requests and responses.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDB(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(UserCreate):
    pass


class RegisterResponse(BaseModel):
    user: User
    access_token: str
    token_type: str = "bearer"
"""
Authentication and authorization dependencies for FastAPI endpoints.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
import asyncpg
from jose import JWTError

from backend.core.dependencies import get_db
from backend.core.auth import decode_access_token
from backend.models.user import User
from backend.schemas.auth import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: asyncpg.Connection = Depends(get_db)
) -> dict:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database connection
        
    Returns:
        Current user dict
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    username: str = payload.get("sub")
    user_id: str = payload.get("user_id")
    
    if username is None or user_id is None:
        raise credentials_exception
        
    # Get user from database
    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )
    
    if user is None:
        raise credentials_exception
        
    return dict(user)


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user dict
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """
    Get current superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        Superuser dict
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Optional authentication - returns None if no token provided
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: asyncpg.Connection = Depends(get_db)
) -> Optional[dict]:
    """
    Get current user if authenticated, otherwise return None.
    
    This is useful for endpoints that should work for both
    authenticated and unauthenticated users.
    """
    if not token:
        return None
        
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
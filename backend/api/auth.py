"""
Authentication API endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import asyncpg
import uuid

from backend.core.dependencies import get_db
from backend.core.config import settings
from backend.core.auth import verify_password, get_password_hash, create_access_token
from backend.core.logger import get_logger
from backend.schemas.auth import (
    Token, User as UserSchema, RegisterRequest, 
    RegisterResponse, LoginRequest
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.fetchrow(
        "SELECT * FROM users WHERE email = $1 OR username = $2",
        request.email, request.username
    )
    
    if existing_user:
        if existing_user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    user_id = uuid.uuid4()
    
    user = await db.fetchrow(
        """
        INSERT INTO users (id, email, username, hashed_password, is_active, is_superuser)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
        """,
        user_id, request.email, request.username, hashed_password,
        request.is_active, request.is_superuser
    )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": str(user["id"])}
    )
    
    logger.info(f"New user registered: {user['username']}")
    
    # Convert to UserSchema
    user_dict = dict(user)
    user_schema = UserSchema(**user_dict)
    
    return RegisterResponse(
        user=user_schema,
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: asyncpg.Connection = Depends(get_db)
):
    """Login user and return access token."""
    # Find user by username or email
    user = await db.fetchrow(
        "SELECT * FROM users WHERE username = $1 OR email = $1",
        form_data.username
    )
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": str(user["id"])},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user['username']}")
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login-json", response_model=Token)
async def login_json(
    request: LoginRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """Login user with JSON payload and return access token."""
    # Find user by username or email
    user = await db.fetchrow(
        "SELECT * FROM users WHERE username = $1 OR email = $1",
        request.username
    )
    
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "user_id": str(user["id"])},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user['username']}")
    
    return Token(access_token=access_token, token_type="bearer")
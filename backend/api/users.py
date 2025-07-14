"""
User management API endpoints.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
import asyncpg

from backend.core.dependencies import get_db
from backend.core.auth_dependencies import get_current_active_user, get_current_superuser
from backend.core.auth import get_password_hash
from backend.core.logger import get_logger
from backend.schemas.auth import User as UserSchema, UserUpdate

logger = get_logger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """Get current user profile."""
    return UserSchema(**current_user)


@router.put("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update current user profile."""
    updates = []
    values = []
    value_count = 1
    
    # Update user fields
    if user_update.email is not None:
        # Check if email is already taken
        existing = await db.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND id != $2",
            user_update.email, current_user["id"]
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        updates.append(f"email = ${value_count}")
        values.append(user_update.email)
        value_count += 1
    
    if user_update.username is not None:
        # Check if username is already taken
        existing = await db.fetchrow(
            "SELECT id FROM users WHERE username = $1 AND id != $2",
            user_update.username, current_user["id"]
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        updates.append(f"username = ${value_count}")
        values.append(user_update.username)
        value_count += 1
    
    if user_update.password is not None:
        updates.append(f"hashed_password = ${value_count}")
        values.append(get_password_hash(user_update.password))
        value_count += 1
    
    # Only superusers can update these fields
    if user_update.is_active is not None or user_update.is_superuser is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update admin fields"
        )
    
    if updates:
        updates.append("updated_at = NOW()")
        values.append(current_user["id"])
        
        query = f"""
            UPDATE users 
            SET {', '.join(updates)}
            WHERE id = ${value_count}
            RETURNING *
        """
        
        updated_user = await db.fetchrow(query, *values)
        logger.info(f"User updated profile: {updated_user['username']}")
        return UserSchema(**dict(updated_user))
    
    return UserSchema(**current_user)


@router.get("/", response_model=List[UserSchema])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_superuser),
    db: asyncpg.Connection = Depends(get_db)
):
    """List all users (superuser only)."""
    users = await db.fetch(
        "SELECT * FROM users OFFSET $1 LIMIT $2",
        skip, limit
    )
    return [UserSchema(**dict(user)) for user in users]


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    db: asyncpg.Connection = Depends(get_db)
):
    """Get user by ID (superuser only)."""
    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserSchema(**dict(user))


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_superuser),
    db: asyncpg.Connection = Depends(get_db)
):
    """Update user by ID (superuser only)."""
    # Check if user exists
    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updates = []
    values = []
    value_count = 1
    
    # Update user fields
    if user_update.email is not None:
        updates.append(f"email = ${value_count}")
        values.append(user_update.email)
        value_count += 1
    if user_update.username is not None:
        updates.append(f"username = ${value_count}")
        values.append(user_update.username)
        value_count += 1
    if user_update.password is not None:
        updates.append(f"hashed_password = ${value_count}")
        values.append(get_password_hash(user_update.password))
        value_count += 1
    if user_update.is_active is not None:
        updates.append(f"is_active = ${value_count}")
        values.append(user_update.is_active)
        value_count += 1
    if user_update.is_superuser is not None:
        updates.append(f"is_superuser = ${value_count}")
        values.append(user_update.is_superuser)
        value_count += 1
    
    if updates:
        updates.append("updated_at = NOW()")
        values.append(user_id)
        
        query = f"""
            UPDATE users 
            SET {', '.join(updates)}
            WHERE id = ${value_count}
            RETURNING *
        """
        
        updated_user = await db.fetchrow(query, *values)
        logger.info(f"Superuser updated user: {updated_user['username']}")
        return UserSchema(**dict(updated_user))
    
    return UserSchema(**dict(user))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_superuser),
    db: asyncpg.Connection = Depends(get_db)
):
    """Delete user by ID (superuser only)."""
    # Check if user exists
    user = await db.fetchrow(
        "SELECT username FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.execute(
        "DELETE FROM users WHERE id = $1",
        user_id
    )
    
    logger.info(f"User deleted: {user['username']}")
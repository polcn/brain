"""
API v1 module exports.
"""
from fastapi import APIRouter
from .health import router as health_router
from .documents import router as documents_router
from .chat import router as chat_router
from backend.api.auth import router as auth_router
from backend.api.users import router as users_router

# Create main v1 router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(documents_router)
api_router.include_router(chat_router)

__all__ = ["api_router"]
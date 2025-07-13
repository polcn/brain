"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.core.database import get_db
from backend.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "version": settings.version
    }


@router.get("/health/db")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Database health check."""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        # Check pgvector extension
        vector_check = await db.execute(
            text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector'")
        )
        has_vector = vector_check.scalar() > 0
        
        return {
            "status": "healthy",
            "database": "connected",
            "pgvector": "enabled" if has_vector else "disabled"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }
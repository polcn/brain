"""Health check endpoints"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.services.vector_store import VectorStore
from backend.services.embeddings import EmbeddingsService
from backend.services.llm import LLMService
from backend.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "brain-api",
        "version": "0.1.0"
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including all dependencies"""
    health_status = {
        "status": "healthy",
        "checks": {
            "database": False,
            "vector_store": False,
            "embeddings_service": False,
            "llm_service": False
        },
        "details": {}
    }
    
    # Check database
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = True
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["details"]["database_error"] = str(e)
    
    # Check vector store
    try:
        vector_store = VectorStore()
        await vector_store.verify_connection(db)
        health_status["checks"]["vector_store"] = True
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["details"]["vector_store_error"] = str(e)
    
    # Check embeddings service
    try:
        embeddings_service = EmbeddingsService()
        test_embedding = await embeddings_service.embed_text("test")
        if test_embedding and len(test_embedding) == 1536:
            health_status["checks"]["embeddings_service"] = True
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["details"]["embeddings_error"] = str(e)
    
    # Check LLM service
    try:
        llm_service = LLMService()
        test_response = await llm_service.generate_response("test", "test")
        if test_response:
            health_status["checks"]["llm_service"] = True
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["details"]["llm_error"] = str(e)
    
    # Set overall status
    if not all(health_status["checks"].values()):
        health_status["status"] = "unhealthy" if not any(health_status["checks"].values()) else "degraded"
    
    return health_status
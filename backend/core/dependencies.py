"""
Dependency injection for FastAPI endpoints.
"""
import asyncpg
from typing import AsyncGenerator

from ..services import VectorStore, EmbeddingsService, LLMService
from ..services.document_processor import DocumentProcessor
from .database import get_db_pool

# Service singletons
_vector_store: VectorStore = None
_embeddings_service: EmbeddingsService = None
_llm_service: LLMService = None
_document_processor: DocumentProcessor = None


async def get_vector_store() -> VectorStore:
    """Get vector store service instance."""
    global _vector_store
    if _vector_store is None:
        pool = await get_db_pool()
        _vector_store = VectorStore(pool)
        await _vector_store.initialize()
    return _vector_store


async def get_embeddings_service() -> EmbeddingsService:
    """Get embeddings service instance."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service


async def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


async def get_document_processor() -> DocumentProcessor:
    """Get document processor instance."""
    global _document_processor
    if _document_processor is None:
        vector_store = await get_vector_store()
        embeddings_service = await get_embeddings_service()
        _document_processor = DocumentProcessor(vector_store, embeddings_service)
    return _document_processor


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get database connection for a request."""
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection
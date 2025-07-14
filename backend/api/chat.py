"""
Chat endpoints for Q&A functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.logger import get_logger
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.chat_service import ChatService

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process a chat query against the documents."""
    try:
        chat_service = ChatService(db)
        response = await chat_service.process_query(request.query)
        return response
        
    except Exception as e:
        logger.error("Chat query failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )
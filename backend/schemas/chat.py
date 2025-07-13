"""
Chat schemas for API requests and responses.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ChatSource(BaseModel):
    document_id: UUID
    document_name: str
    chunk_content: str
    similarity_score: float


class ChatRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[ChatSource]
    model_used: str
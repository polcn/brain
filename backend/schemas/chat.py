"""
Chat schemas for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatSource(BaseModel):
    document_id: UUID
    document_name: str
    chunk_content: str
    similarity_score: float


class ChatRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None
    sources: Optional[List[ChatSource]] = None


class ChatCompletionRequest(BaseModel):
    messages: List[ChatMessage]
    document_ids: Optional[List[UUID]] = None
    max_results: Optional[int] = 5
    stream: Optional[bool] = False


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


class ChatResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    query: str
    answer: str
    sources: List[ChatSource]
    model_used: str


class SearchResult(BaseModel):
    document_id: UUID
    document_name: str
    chunk_content: str
    chunk_id: UUID
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[UUID]] = None
    max_results: Optional[int] = 10
    threshold: Optional[float] = 0.7


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
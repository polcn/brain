"""
Document schemas for API requests and responses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class DocumentStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentProcessingStatus(BaseModel):
    status: DocumentStatus
    progress: Optional[float] = None
    message: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    status: DocumentStatus
    message: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_name: str
    file_size: Optional[int]
    content_type: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int
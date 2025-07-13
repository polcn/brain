"""
Document management API endpoints.
"""
import os
import logging
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncpg

from ...schemas.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentProcessingStatus
)
from ...models.document import Document
from ...core.config import settings
from ...core.dependencies import (
    get_db,
    get_document_processor,
    get_vector_store
)
from ...services.document_processor import DocumentProcessor
from ...services.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: asyncpg.Connection = Depends(get_db),
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Upload and process a new document."""
    # Validate file
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_file_size} bytes"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"File type not supported. Allowed types: {settings.allowed_extensions}"
        )
    
    # Create document record
    document_id = uuid4()
    
    try:
        # Read file content
        content = await file.read()
        
        # Insert document record
        await db.execute(
            """
            INSERT INTO documents (id, name, mime_type, size, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            document_id,
            file.filename,
            file.content_type,
            len(content),
            "processing"
        )
        
        # Process document asynchronously
        # In production, this would be queued
        result = await document_processor.process_document(
            file_content=content,
            filename=file.filename,
            document_id=document_id,
            mime_type=file.content_type
        )
        
        # Update document status
        await db.execute(
            """
            UPDATE documents 
            SET status = $1, 
                s3_key = $2,
                processed_at = $3,
                chunk_count = $4
            WHERE id = $5
            """,
            result['status'],
            result['s3_key'],
            datetime.utcnow(),
            result['chunk_count'],
            document_id
        )
        
        # Fetch updated document
        row = await db.fetchrow(
            "SELECT * FROM documents WHERE id = $1",
            document_id
        )
        
        return DocumentResponse(
            id=row['id'],
            name=row['name'],
            mime_type=row['mime_type'],
            size=row['size'],
            status=row['status'],
            chunk_count=row['chunk_count'],
            created_at=row['created_at'],
            processed_at=row['processed_at']
        )
        
    except Exception as e:
        # Update status to failed
        await db.execute(
            """
            UPDATE documents 
            SET status = 'failed', 
                error_message = $1
            WHERE id = $2
            """,
            str(e),
            document_id
        )
        
        logger.error(f"Failed to process document {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[DocumentProcessingStatus] = None,
    db: asyncpg.Connection = Depends(get_db)
):
    """List all documents with optional filtering."""
    # Build query
    query = "SELECT * FROM documents"
    params = []
    
    if status:
        query += " WHERE status = $1"
        params.append(status)
    
    query += " ORDER BY created_at DESC"
    
    # Get total count
    count_query = "SELECT COUNT(*) FROM documents"
    if status:
        count_query += " WHERE status = $1"
    
    total = await db.fetchval(count_query, *params)
    
    # Add pagination
    params.extend([limit, skip])
    query += f" LIMIT ${len(params)-1} OFFSET ${len(params)}"
    
    # Fetch documents
    rows = await db.fetch(query, *params)
    
    documents = [
        DocumentResponse(
            id=row['id'],
            name=row['name'],
            mime_type=row['mime_type'],
            size=row['size'],
            status=row['status'],
            chunk_count=row['chunk_count'],
            created_at=row['created_at'],
            processed_at=row['processed_at']
        )
        for row in rows
    ]
    
    return DocumentListResponse(
        documents=documents,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: asyncpg.Connection = Depends(get_db)
):
    """Get a specific document by ID."""
    row = await db.fetchrow(
        "SELECT * FROM documents WHERE id = $1",
        document_id
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=row['id'],
        name=row['name'],
        mime_type=row['mime_type'],
        size=row['size'],
        status=row['status'],
        chunk_count=row['chunk_count'],
        created_at=row['created_at'],
        processed_at=row['processed_at']
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
    vector_store: VectorStore = Depends(get_vector_store),
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Delete a document and all associated data."""
    # Check if document exists
    row = await db.fetchrow(
        "SELECT id, s3_key FROM documents WHERE id = $1",
        document_id
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete from vector store
        await vector_store.delete_document_vectors(document_id)
        
        # Delete from S3
        if row['s3_key']:
            await document_processor.delete_from_s3(row['s3_key'])
        
        # Delete from database
        await db.execute(
            "DELETE FROM documents WHERE id = $1",
            document_id
        )
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: asyncpg.Connection = Depends(get_db),
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Download the processed (redacted) document."""
    # Get document info
    row = await db.fetchrow(
        "SELECT name, s3_key, mime_type FROM documents WHERE id = $1",
        document_id
    )
    
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not row['s3_key']:
        raise HTTPException(
            status_code=404,
            detail="Document has not been processed yet"
        )
    
    try:
        # Download from S3
        content = await document_processor.download_from_s3(row['s3_key'])
        
        # Return as streaming response
        return StreamingResponse(
            content=content,
            media_type=row['mime_type'],
            headers={
                "Content-Disposition": f"attachment; filename={row['name']}"
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to download document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download document: {str(e)}"
        )
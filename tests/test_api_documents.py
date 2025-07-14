"""
Tests for document API endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import json
from datetime import datetime

from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
class TestDocumentAPI:
    """Test document API endpoints."""
    
    @pytest.fixture
    def mock_document_processor(self):
        """Mock document processor service."""
        processor = Mock()
        processor.process_document = AsyncMock(
            return_value={
                "status": "success",
                "chunks_created": 5,
                "s3_key": "documents/123/test.pdf",
                "original_s3_key": "originals/123/test.pdf"
            }
        )
        return processor
    
    @pytest.fixture
    def mock_pool(self):
        """Mock database pool."""
        pool = Mock()
        
        # Mock connection
        conn = AsyncMock()
        conn.fetchone = AsyncMock()
        conn.fetchval = AsyncMock()
        conn.fetch = AsyncMock()
        conn.execute = AsyncMock()
        
        # Mock transaction
        conn.transaction = AsyncMock()
        conn.transaction.return_value.__aenter__ = AsyncMock()
        conn.transaction.return_value.__aexit__ = AsyncMock()
        
        pool.acquire = AsyncMock()
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock()
        
        return pool
    
    async def test_upload_document_success(self, client: AsyncClient, mock_pool, mock_document_processor):
        """Test successful document upload."""
        # Mock database responses
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchone.return_value = {
            "id": uuid4(),
            "name": "test.pdf",
            "mime_type": "application/pdf",
            "size": 1024,
            "status": "processed",
            "chunk_count": 5,
            "created_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            with patch("backend.api.v1.documents.get_document_processor", 
                      return_value=mock_document_processor):
                
                # Create test file
                files = {"file": ("test.pdf", b"PDF content", "application/pdf")}
                
                response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "test.pdf"
        assert data["status"] == "processed"
        assert data["chunk_count"] == 5
    
    async def test_upload_document_invalid_type(self, client: AsyncClient):
        """Test upload with invalid file type."""
        files = {"file": ("test.exe", b"EXE content", "application/octet-stream")}
        
        response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        assert "Unsupported file type" in response.json()["detail"]
    
    async def test_upload_document_too_large(self, client: AsyncClient):
        """Test upload with file too large."""
        # Create large content (over 10MB)
        large_content = b"x" * (11 * 1024 * 1024)
        files = {"file": ("large.pdf", large_content, "application/pdf")}
        
        response = await client.post("/api/v1/documents/upload", files=files)
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        assert "File too large" in response.json()["detail"]
    
    async def test_list_documents(self, client: AsyncClient, mock_pool):
        """Test listing documents."""
        # Mock database response
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch.return_value = [
            {
                "id": uuid4(),
                "name": "doc1.pdf",
                "mime_type": "application/pdf",
                "size": 1024,
                "status": "processed",
                "chunk_count": 5,
                "created_at": datetime.utcnow(),
                "processed_at": datetime.utcnow()
            },
            {
                "id": uuid4(),
                "name": "doc2.txt",
                "mime_type": "text/plain",
                "size": 512,
                "status": "processed",
                "chunk_count": 2,
                "created_at": datetime.utcnow(),
                "processed_at": datetime.utcnow()
            }
        ]
        mock_conn.fetchval.return_value = 2  # Total count
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            response = await client.get("/api/v1/documents?skip=0&limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["documents"]) == 2
        assert data["total"] == 2
        assert data["documents"][0]["name"] == "doc1.pdf"
    
    async def test_list_documents_with_filter(self, client: AsyncClient, mock_pool):
        """Test listing documents with status filter."""
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetch.return_value = []
        mock_conn.fetchval.return_value = 0
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            response = await client.get("/api/v1/documents?status=processing")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify filter was applied in query
        call_args = mock_conn.fetch.call_args[0][0]
        assert "WHERE status = $3" in call_args
    
    async def test_get_document(self, client: AsyncClient, mock_pool):
        """Test getting single document."""
        doc_id = uuid4()
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchone.return_value = {
            "id": doc_id,
            "name": "test.pdf",
            "mime_type": "application/pdf",
            "size": 1024,
            "status": "processed",
            "chunk_count": 5,
            "created_at": datetime.utcnow(),
            "processed_at": datetime.utcnow()
        }
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            response = await client.get(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(doc_id)
        assert data["name"] == "test.pdf"
    
    async def test_get_document_not_found(self, client: AsyncClient, mock_pool):
        """Test getting non-existent document."""
        doc_id = uuid4()
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchone.return_value = None
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            response = await client.get(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Document not found" in response.json()["detail"]
    
    async def test_delete_document(self, client: AsyncClient, mock_pool):
        """Test deleting document."""
        doc_id = uuid4()
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchone.return_value = {
            "id": doc_id,
            "s3_key": "documents/123/test.pdf",
            "original_s3_key": "originals/123/test.pdf"
        }
        
        mock_s3 = Mock()
        mock_s3.delete_object = AsyncMock()
        
        mock_vector_store = Mock()
        mock_vector_store.delete_document_vectors = AsyncMock(return_value=5)
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            with patch("backend.api.v1.documents.get_s3_client", return_value=mock_s3):
                with patch("backend.api.v1.documents.get_vector_store", 
                          return_value=mock_vector_store):
                    response = await client.delete(f"/api/v1/documents/{doc_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]
        
        # Verify S3 deletions
        assert mock_s3.delete_object.call_count == 2
        
        # Verify vector deletion
        mock_vector_store.delete_document_vectors.assert_called_once_with(doc_id)
    
    async def test_download_document(self, client: AsyncClient, mock_pool):
        """Test downloading document."""
        doc_id = uuid4()
        mock_conn = mock_pool.acquire.return_value.__aenter__.return_value
        mock_conn.fetchone.return_value = {
            "id": doc_id,
            "name": "test.pdf",
            "mime_type": "application/pdf",
            "s3_key": "documents/123/test.pdf"
        }
        
        mock_s3 = Mock()
        mock_s3.get_object = AsyncMock(
            return_value={
                "Body": AsyncMock(read=AsyncMock(return_value=b"PDF content"))
            }
        )
        
        with patch("backend.api.v1.documents.get_db_pool", return_value=mock_pool):
            with patch("backend.api.v1.documents.get_s3_client", return_value=mock_s3):
                response = await client.get(f"/api/v1/documents/{doc_id}/download")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert response.headers["content-disposition"] == 'attachment; filename="test.pdf"'
        assert response.content == b"PDF content"
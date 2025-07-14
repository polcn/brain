"""
Tests for document processor service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import os
from uuid import uuid4
import numpy as np

from backend.services.document_processor import DocumentProcessorService


@pytest.mark.asyncio
class TestDocumentProcessorService:
    """Test document processor service functionality."""
    
    @pytest.fixture
    def mock_dependencies(self, mock_embeddings_service, mock_llm_service, mock_s3_client):
        """Create mock dependencies."""
        mock_pool = Mock()
        mock_vector_store = Mock()
        mock_vector_store.upsert_vectors = AsyncMock(return_value=True)
        
        return {
            "pool": mock_pool,
            "s3_client": mock_s3_client,
            "vector_store": mock_vector_store,
            "embeddings_service": mock_embeddings_service,
            "llm_service": mock_llm_service
        }
    
    @pytest.fixture
    def service(self, mock_dependencies):
        """Create document processor service with mocks."""
        return DocumentProcessorService(
            pool=mock_dependencies["pool"],
            s3_client=mock_dependencies["s3_client"],
            vector_store=mock_dependencies["vector_store"],
            embeddings_service=mock_dependencies["embeddings_service"],
            llm_service=mock_dependencies["llm_service"]
        )
    
    async def test_process_pdf_document(self, service, sample_pdf_content, mock_dependencies):
        """Test processing PDF document."""
        document_id = uuid4()
        
        # Mock file operations
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.pdf"
            mock_temp.return_value.__enter__.return_value = mock_file
            
            # Mock redaction subprocess
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Redacted successfully"
                
                # Mock PDF reading
                with patch("backend.services.document_processor.fitz") as mock_fitz:
                    mock_doc = Mock()
                    mock_page = Mock()
                    mock_page.get_text.return_value = "This is test content from PDF."
                    mock_doc.__iter__.return_value = [mock_page]
                    mock_doc.__len__.return_value = 1
                    mock_fitz.open.return_value.__enter__.return_value = mock_doc
                    
                    # Process document
                    result = await service.process_document(
                        sample_pdf_content,
                        "test.pdf",
                        document_id,
                        "application/pdf"
                    )
        
        # Verify result
        assert result["status"] == "success"
        assert result["chunks_created"] > 0
        assert "s3_key" in result
        assert "original_s3_key" in result
        
        # Verify S3 uploads
        assert mock_dependencies["s3_client"].put_object.call_count == 2
        
        # Verify embeddings were generated
        mock_dependencies["embeddings_service"].generate_embeddings.assert_called()
        
        # Verify vectors were stored
        mock_dependencies["vector_store"].upsert_vectors.assert_called()
    
    async def test_process_text_document(self, service, sample_txt_content, mock_dependencies):
        """Test processing text document."""
        document_id = uuid4()
        
        with patch("tempfile.NamedTemporaryFile") as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.txt"
            mock_temp.return_value.__enter__.return_value = mock_file
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                
                # Mock reading redacted file
                with patch("builtins.open", create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = (
                        sample_txt_content.decode()
                    )
                    
                    result = await service.process_document(
                        sample_txt_content,
                        "test.txt",
                        document_id,
                        "text/plain"
                    )
        
        assert result["status"] == "success"
        assert result["chunks_created"] > 0
    
    async def test_validate_file_type(self, service):
        """Test file type validation."""
        # Valid types
        assert service._validate_file_type("test.pdf", "application/pdf") is True
        assert service._validate_file_type("test.txt", "text/plain") is True
        assert service._validate_file_type("test.docx", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document") is True
        
        # Invalid types
        assert service._validate_file_type("test.exe", "application/octet-stream") is False
        assert service._validate_file_type("test.jpg", "image/jpeg") is False
    
    async def test_redact_document_success(self, service):
        """Test successful document redaction."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name
        
        try:
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "Redaction complete"
                
                output_path = await service._redact_document(tmp_path)
                
                assert output_path.endswith("_redacted.pdf")
                mock_run.assert_called_once()
                
                # Check command structure
                call_args = mock_run.call_args[0][0]
                assert "redact" in call_args
                assert tmp_path in call_args
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    async def test_redact_document_failure(self, service):
        """Test document redaction failure."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Redaction failed"
            
            with pytest.raises(Exception, match="Redaction failed"):
                await service._redact_document("/tmp/test.pdf")
    
    async def test_chunk_text(self, service):
        """Test text chunking."""
        # Create text with clear boundaries
        text = "First sentence. " * 100  # Long text
        
        chunks = service._chunk_text(text, chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        
        # Verify chunk properties
        for i, chunk in enumerate(chunks):
            assert "content" in chunk
            assert "start_char" in chunk
            assert "end_char" in chunk
            assert "chunk_index" in chunk
            assert chunk["chunk_index"] == i
            
            # Verify overlap
            if i > 0:
                prev_end = chunks[i-1]["end_char"]
                curr_start = chunk["start_char"]
                assert curr_start < prev_end  # Should have overlap
    
    async def test_extract_text_from_pdf(self, service):
        """Test PDF text extraction."""
        with patch("backend.services.document_processor.fitz") as mock_fitz:
            # Mock PDF document
            mock_doc = Mock()
            mock_page1 = Mock()
            mock_page1.get_text.return_value = "Page 1 content"
            mock_page2 = Mock()
            mock_page2.get_text.return_value = "Page 2 content"
            
            mock_doc.__iter__.return_value = [mock_page1, mock_page2]
            mock_doc.__len__.return_value = 2
            mock_fitz.open.return_value.__enter__.return_value = mock_doc
            
            text, metadata = await service._extract_text_from_pdf("/tmp/test.pdf")
            
            assert "Page 1 content" in text
            assert "Page 2 content" in text
            assert metadata["pages"] == 2
            assert metadata["file_type"] == "pdf"
    
    async def test_process_document_with_metadata(self, service, mock_dependencies):
        """Test that metadata is preserved through processing."""
        document_id = uuid4()
        
        with patch.multiple(
            service,
            _validate_file_type=Mock(return_value=True),
            _save_temp_file=AsyncMock(return_value="/tmp/test.pdf"),
            _redact_document=AsyncMock(return_value="/tmp/test_redacted.pdf"),
            _extract_text_from_pdf=AsyncMock(
                return_value=("Test content", {"pages": 1, "file_type": "pdf"})
            ),
            _chunk_text=Mock(return_value=[
                {"content": "chunk1", "chunk_index": 0, "start_char": 0, "end_char": 10}
            ])
        ):
            with patch("builtins.open", create=True):
                result = await service.process_document(
                    b"content",
                    "test.pdf",
                    document_id,
                    "application/pdf"
                )
        
        # Verify metadata was included in vector storage
        call_args = mock_dependencies["vector_store"].upsert_vectors.call_args
        vectors = call_args[0][1]
        
        for _, _, metadata in vectors:
            assert "chunk_metadata" in metadata
            assert metadata["chunk_metadata"]["pages"] == 1
            assert metadata["chunk_metadata"]["file_type"] == "pdf"
    
    async def test_process_empty_document(self, service):
        """Test handling empty document."""
        document_id = uuid4()
        
        with patch.multiple(
            service,
            _validate_file_type=Mock(return_value=True),
            _save_temp_file=AsyncMock(return_value="/tmp/test.txt"),
            _redact_document=AsyncMock(return_value="/tmp/test_redacted.txt"),
            _extract_text_from_file=AsyncMock(return_value=("", {}))
        ):
            with pytest.raises(ValueError, match="empty"):
                await service.process_document(
                    b"",
                    "empty.txt",
                    document_id,
                    "text/plain"
                )
    
    async def test_cleanup_on_error(self, service):
        """Test that temporary files are cleaned up on error."""
        temp_files = []
        
        async def mock_save_temp(content):
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                temp_files.append(tmp.name)
                return tmp.name
        
        with patch.object(service, "_save_temp_file", side_effect=mock_save_temp):
            with patch.object(service, "_redact_document", 
                            side_effect=Exception("Redaction error")):
                
                with pytest.raises(Exception):
                    await service.process_document(
                        b"content",
                        "test.pdf",
                        uuid4(),
                        "application/pdf"
                    )
        
        # Verify temp files were cleaned up
        for temp_file in temp_files:
            assert not os.path.exists(temp_file)
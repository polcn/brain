"""
Tests for embeddings service.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
import json

from backend.services.embeddings import EmbeddingsService


@pytest.mark.asyncio
class TestEmbeddingsService:
    """Test embeddings service functionality."""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Create mock Bedrock client."""
        client = Mock()
        
        # Mock successful embedding response
        async def mock_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            input_text = body.get("inputText", "")
            
            # Return mock embedding
            response_body = json.dumps({
                "embedding": np.random.rand(1536).tolist(),
                "inputTextTokenCount": len(input_text.split())
            })
            
            return {
                "body": Mock(read=Mock(return_value=response_body.encode()))
            }
        
        client.invoke_model = AsyncMock(side_effect=mock_invoke_model)
        return client
    
    async def test_generate_embedding(self, mock_bedrock_client):
        """Test generating single embedding."""
        service = EmbeddingsService(mock_bedrock_client)
        
        text = "This is a test document"
        embedding = await service.generate_embedding(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (1536,)
        assert np.linalg.norm(embedding) == pytest.approx(1.0, rel=1e-5)  # Normalized
        
        # Verify Bedrock was called
        mock_bedrock_client.invoke_model.assert_called_once()
    
    async def test_generate_embeddings_batch(self, mock_bedrock_client):
        """Test generating multiple embeddings."""
        service = EmbeddingsService(mock_bedrock_client)
        
        texts = ["First text", "Second text", "Third text"]
        embeddings = await service.generate_embeddings(texts)
        
        assert len(embeddings) == 3
        for embedding in embeddings:
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (1536,)
            assert np.linalg.norm(embedding) == pytest.approx(1.0, rel=1e-5)
        
        # Should be called once per text
        assert mock_bedrock_client.invoke_model.call_count == 3
    
    async def test_generate_embeddings_large_batch(self, mock_bedrock_client):
        """Test generating embeddings for large batch."""
        service = EmbeddingsService(mock_bedrock_client)
        
        # Create batch larger than max batch size (25)
        texts = [f"Text {i}" for i in range(30)]
        embeddings = await service.generate_embeddings(texts)
        
        assert len(embeddings) == 30
        # Should process in batches
        assert mock_bedrock_client.invoke_model.call_count == 30
    
    async def test_generate_embeddings_empty_text(self, mock_bedrock_client):
        """Test handling empty text."""
        service = EmbeddingsService(mock_bedrock_client)
        
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("")
        
        with pytest.raises(ValueError, match="No texts provided"):
            await service.generate_embeddings([])
    
    async def test_generate_embeddings_without_normalization(self, mock_bedrock_client):
        """Test generating embeddings without normalization."""
        # Mock to return non-normalized embedding
        async def mock_invoke_model(**kwargs):
            response_body = json.dumps({
                "embedding": [2.0] * 1536,  # Non-normalized
                "inputTextTokenCount": 5
            })
            return {
                "body": Mock(read=Mock(return_value=response_body.encode()))
            }
        
        mock_bedrock_client.invoke_model = AsyncMock(side_effect=mock_invoke_model)
        service = EmbeddingsService(mock_bedrock_client)
        
        embedding = await service.generate_embedding("test", normalize=False)
        
        # Should not be normalized
        assert np.linalg.norm(embedding) > 1.0
    
    async def test_estimate_tokens(self):
        """Test token estimation."""
        service = EmbeddingsService(Mock())
        
        # Single text
        tokens = service.estimate_tokens("This is a test sentence.")
        assert tokens == 5  # Rough estimate
        
        # Multiple texts
        tokens = service.estimate_tokens(["First sentence.", "Second sentence."])
        assert tokens == 4  # 2 + 2
    
    async def test_health_check_success(self, mock_bedrock_client):
        """Test successful health check."""
        service = EmbeddingsService(mock_bedrock_client)
        
        health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["model"] == "amazon.titan-embed-text-v1"
        assert "test_embedding_dimensions" in health
        assert health["test_embedding_dimensions"] == 1536
    
    async def test_health_check_failure(self):
        """Test health check with failure."""
        # Mock client that raises exception
        mock_client = Mock()
        mock_client.invoke_model = AsyncMock(side_effect=Exception("Connection error"))
        
        service = EmbeddingsService(mock_client)
        health = await service.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health
        assert "Connection error" in health["error"]
    
    async def test_retry_on_throttling(self):
        """Test retry logic on throttling errors."""
        mock_client = Mock()
        call_count = 0
        
        async def mock_invoke_with_throttle(**kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                # Simulate throttling error
                raise Exception("ThrottlingException")
            
            # Success on third attempt
            response_body = json.dumps({
                "embedding": np.random.rand(1536).tolist(),
                "inputTextTokenCount": 5
            })
            return {
                "body": Mock(read=Mock(return_value=response_body.encode()))
            }
        
        mock_client.invoke_model = AsyncMock(side_effect=mock_invoke_with_throttle)
        service = EmbeddingsService(mock_client)
        
        # Should succeed after retries
        embedding = await service.generate_embedding("test")
        assert isinstance(embedding, np.ndarray)
        assert call_count == 3
    
    async def test_long_text_truncation(self, mock_bedrock_client):
        """Test handling of long text."""
        service = EmbeddingsService(mock_bedrock_client)
        
        # Create text longer than token limit
        long_text = " ".join(["word"] * 10000)
        
        # Should truncate and still generate embedding
        embedding = await service.generate_embedding(long_text)
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (1536,)
        
        # Check that text was truncated in the call
        call_args = mock_bedrock_client.invoke_model.call_args
        body = json.loads(call_args[1]["body"])
        assert len(body["inputText"]) < len(long_text)
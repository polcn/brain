"""
Tests for LLM service.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json

from backend.services.llm import LLMService


@pytest.mark.asyncio
class TestLLMService:
    """Test LLM service functionality."""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """Create mock Bedrock client."""
        client = Mock()
        
        # Mock successful response
        async def mock_invoke_model(**kwargs):
            body = json.loads(kwargs["body"])
            
            # Return mock response based on prompt
            if "summarize" in body.get("prompt", "").lower():
                response_text = "This document discusses important topics."
            elif "topics" in body.get("prompt", "").lower():
                response_text = "1. Machine Learning\\n2. Data Processing\\n3. API Development"
            else:
                response_text = "Based on the provided context, here is the answer to your query."
            
            response_body = json.dumps({
                "completion": response_text,
                "stop_reason": "stop_sequence"
            })
            
            return {
                "body": Mock(read=Mock(return_value=response_body.encode()))
            }
        
        client.invoke_model = AsyncMock(side_effect=mock_invoke_model)
        return client
    
    @pytest.fixture
    def mock_bedrock_client_streaming(self):
        """Create mock Bedrock client with streaming support."""
        client = Mock()
        
        # Mock streaming response
        async def mock_invoke_model_stream(**kwargs):
            response_text = "This is a streaming response"
            
            # Create mock event stream
            class MockEventStream:
                def __init__(self, text):
                    self.words = text.split()
                    self.index = 0
                
                def __aiter__(self):
                    return self
                
                async def __anext__(self):
                    if self.index >= len(self.words):
                        raise StopAsyncIteration
                    
                    word = self.words[self.index]
                    self.index += 1
                    
                    event = {
                        "chunk": {
                            "bytes": json.dumps({
                                "completion": word + " "
                            }).encode()
                        }
                    }
                    return event
            
            return {"body": MockEventStream(response_text)}
        
        client.invoke_model_with_response_stream = AsyncMock(
            side_effect=mock_invoke_model_stream
        )
        return client
    
    async def test_generate_response(self, mock_bedrock_client):
        """Test generating response."""
        service = LLMService(mock_bedrock_client)
        
        query = "What is machine learning?"
        context_chunks = [
            {
                "content": "Machine learning is a subset of AI.",
                "metadata": {"source": "doc1.pdf"}
            }
        ]
        
        response = await service.generate_response(query, context_chunks)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert mock_bedrock_client.invoke_model.called
    
    async def test_generate_response_with_chat_history(self, mock_bedrock_client):
        """Test generating response with chat history."""
        service = LLMService(mock_bedrock_client)
        
        query = "Can you elaborate on that?"
        context_chunks = [{"content": "Additional context", "metadata": {}}]
        chat_history = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence."}
        ]
        
        response = await service.generate_response(
            query, context_chunks, chat_history=chat_history
        )
        
        assert isinstance(response, str)
        
        # Check that chat history was included in prompt
        call_args = mock_bedrock_client.invoke_model.call_args
        body = json.loads(call_args[1]["body"])
        assert "What is AI?" in body["prompt"]
        assert "AI is artificial intelligence" in body["prompt"]
    
    async def test_generate_response_streaming(self, mock_bedrock_client_streaming):
        """Test streaming response generation."""
        service = LLMService(mock_bedrock_client_streaming)
        
        query = "Explain streaming"
        context_chunks = [{"content": "Streaming context", "metadata": {}}]
        
        response_gen = await service.generate_response(
            query, context_chunks, stream=True
        )
        
        # Collect streamed response
        full_response = ""
        async for chunk in response_gen:
            assert isinstance(chunk, str)
            full_response += chunk
        
        assert full_response == "This is a streaming response "
    
    async def test_summarize_document(self, mock_bedrock_client):
        """Test document summarization."""
        service = LLMService(mock_bedrock_client)
        
        chunks = [
            {"content": "First paragraph about topic A.", "metadata": {}},
            {"content": "Second paragraph about topic B.", "metadata": {}},
            {"content": "Conclusion combining A and B.", "metadata": {}}
        ]
        
        summary = await service.summarize_document(chunks, max_length=100)
        
        assert isinstance(summary, str)
        assert "document" in summary.lower()
        assert len(summary) <= 200  # Reasonable length
    
    async def test_extract_topics(self, mock_bedrock_client):
        """Test topic extraction."""
        service = LLMService(mock_bedrock_client)
        
        chunks = [
            {"content": "Machine learning algorithms process data.", "metadata": {}},
            {"content": "API endpoints handle HTTP requests.", "metadata": {}},
        ]
        
        topics = await service.extract_topics(chunks, max_topics=5)
        
        assert isinstance(topics, list)
        assert len(topics) <= 5
        assert all(isinstance(topic, str) for topic in topics)
    
    async def test_health_check_success(self, mock_bedrock_client):
        """Test successful health check."""
        service = LLMService(mock_bedrock_client)
        
        health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["model"] == "anthropic.claude-instant-v1"
        assert "test_response" in health
    
    async def test_health_check_failure(self):
        """Test health check with failure."""
        mock_client = Mock()
        mock_client.invoke_model = AsyncMock(
            side_effect=Exception("Model not available")
        )
        
        service = LLMService(mock_client)
        health = await service.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health
        assert "Model not available" in health["error"]
    
    async def test_empty_context(self, mock_bedrock_client):
        """Test handling empty context."""
        service = LLMService(mock_bedrock_client)
        
        response = await service.generate_response(
            "Query without context",
            []  # Empty context
        )
        
        assert isinstance(response, str)
        # Should handle gracefully
        assert len(response) > 0
    
    async def test_prompt_construction(self, mock_bedrock_client):
        """Test proper prompt construction."""
        service = LLMService(mock_bedrock_client)
        
        query = "What is the capital?"
        context_chunks = [
            {
                "content": "France is a country in Europe.",
                "metadata": {"source": "geography.pdf", "page": 10}
            },
            {
                "content": "The capital of France is Paris.",
                "metadata": {"source": "geography.pdf", "page": 11}
            }
        ]
        
        await service.generate_response(query, context_chunks)
        
        # Verify prompt structure
        call_args = mock_bedrock_client.invoke_model.call_args
        body = json.loads(call_args[1]["body"])
        prompt = body["prompt"]
        
        assert "What is the capital?" in prompt
        assert "France is a country" in prompt
        assert "The capital of France is Paris" in prompt
        assert "Human:" in prompt
        assert "Assistant:" in prompt
    
    async def test_max_tokens_limit(self, mock_bedrock_client):
        """Test token limit handling."""
        service = LLMService(mock_bedrock_client)
        
        # Create very long context
        long_chunks = [
            {"content": "x" * 1000, "metadata": {}}
            for _ in range(10)
        ]
        
        # Should handle without error
        response = await service.generate_response(
            "Summarize", long_chunks
        )
        
        assert isinstance(response, str)
        
        # Check that max_tokens was set appropriately
        call_args = mock_bedrock_client.invoke_model.call_args
        body = json.loads(call_args[1]["body"])
        assert body["max_tokens_to_sample"] <= 4096
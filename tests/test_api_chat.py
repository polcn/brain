"""
Tests for chat API endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import json
import asyncio

from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
class TestChatAPI:
    """Test chat API endpoints."""
    
    @pytest.fixture
    def mock_services(self, mock_embeddings_service, mock_llm_service):
        """Mock services for chat endpoints."""
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.similarity_search = AsyncMock(
            return_value=[
                (uuid4(), "Relevant content about the topic", 0.92, 
                 {"source": "doc1.pdf", "page": 1}),
                (uuid4(), "Additional information", 0.85,
                 {"source": "doc2.pdf", "page": 3})
            ]
        )
        
        # Mock pool for document name lookup
        mock_pool = Mock()
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(
            return_value=[
                {"id": uuid4(), "name": "doc1.pdf"},
                {"id": uuid4(), "name": "doc2.pdf"}
            ]
        )
        
        mock_pool.acquire = AsyncMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock()
        
        return {
            "pool": mock_pool,
            "vector_store": mock_vector_store,
            "embeddings_service": mock_embeddings_service,
            "llm_service": mock_llm_service
        }
    
    async def test_chat_query(self, client: AsyncClient, mock_services):
        """Test basic chat query."""
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store", 
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    with patch("backend.api.v1.chat.get_llm_service",
                              return_value=mock_services["llm_service"]):
                        
                        response = await client.post(
                            "/api/v1/chat",
                            json={"query": "What is machine learning?"}
                        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert len(data["sources"]) > 0
        assert data["confidence"] > 0
    
    async def test_chat_query_with_filters(self, client: AsyncClient, mock_services):
        """Test chat query with document filters."""
        doc_ids = [str(uuid4()) for _ in range(2)]
        
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    with patch("backend.api.v1.chat.get_llm_service",
                              return_value=mock_services["llm_service"]):
                        
                        response = await client.post(
                            "/api/v1/chat",
                            json={
                                "query": "Explain the concept",
                                "document_ids": doc_ids,
                                "max_results": 3,
                                "similarity_threshold": 0.8
                            }
                        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify filters were passed to similarity search
        call_args = mock_services["vector_store"].similarity_search.call_args
        assert call_args[1]["filter_document_ids"] is not None
        assert call_args[1]["k"] == 3
        assert call_args[1]["threshold"] == 0.8
    
    async def test_chat_with_history(self, client: AsyncClient, mock_services):
        """Test chat with conversation history."""
        chat_history = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence."}
        ]
        
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    with patch("backend.api.v1.chat.get_llm_service",
                              return_value=mock_services["llm_service"]):
                        
                        response = await client.post(
                            "/api/v1/chat",
                            json={
                                "query": "Can you elaborate?",
                                "chat_history": chat_history
                            }
                        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify history was passed to LLM
        call_args = mock_services["llm_service"].generate_response.call_args
        assert call_args[1]["chat_history"] == chat_history
    
    async def test_search_endpoint(self, client: AsyncClient, mock_services):
        """Test search-only endpoint."""
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    
                    response = await client.post(
                        "/api/v1/chat/search",
                        json={"query": "machine learning algorithms"}
                    )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0
        assert "chunk_id" in data["results"][0]
        assert "content" in data["results"][0]
        assert "similarity_score" in data["results"][0]
        assert data["results"][0]["similarity_score"] > 0
    
    async def test_empty_search_results(self, client: AsyncClient, mock_services):
        """Test handling of empty search results."""
        # Mock empty search results
        mock_services["vector_store"].similarity_search = AsyncMock(return_value=[])
        
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    with patch("backend.api.v1.chat.get_llm_service",
                              return_value=mock_services["llm_service"]):
                        
                        response = await client.post(
                            "/api/v1/chat",
                            json={"query": "obscure topic"}
                        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should still provide a response, but indicate low confidence
        assert data["confidence"] < 0.5
        assert len(data["sources"]) == 0
    
    async def test_stream_chat(self, client: AsyncClient, mock_services):
        """Test streaming chat response."""
        # Mock streaming response
        async def mock_stream():
            for word in ["This", "is", "streaming", "response"]:
                yield word + " "
        
        mock_services["llm_service"].generate_response = AsyncMock(
            return_value=mock_stream()
        )
        
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    with patch("backend.api.v1.chat.get_llm_service",
                              return_value=mock_services["llm_service"]):
                        
                        response = await client.post(
                            "/api/v1/chat/stream",
                            json={"query": "Stream this response"}
                        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/event-stream"
        
        # Parse SSE response
        content = response.content.decode()
        assert "data: " in content
        assert "This" in content
        assert "streaming" in content
    
    @pytest.mark.skip(reason="WebSocket testing requires special setup")
    async def test_websocket_chat(self, client: AsyncClient, mock_services):
        """Test WebSocket chat endpoint."""
        # WebSocket testing requires websocket client setup
        pass
    
    async def test_invalid_query(self, client: AsyncClient):
        """Test invalid query handling."""
        # Empty query
        response = await client.post("/api/v1/chat", json={"query": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing query
        response = await client.post("/api/v1/chat", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_invalid_document_ids(self, client: AsyncClient):
        """Test invalid document ID format."""
        response = await client.post(
            "/api/v1/chat",
            json={
                "query": "test",
                "document_ids": ["not-a-uuid"]
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_error_handling(self, client: AsyncClient, mock_services):
        """Test error handling in chat endpoint."""
        # Mock an error in vector search
        mock_services["vector_store"].similarity_search = AsyncMock(
            side_effect=Exception("Database connection error")
        )
        
        with patch("backend.api.v1.chat.get_db_pool", return_value=mock_services["pool"]):
            with patch("backend.api.v1.chat.get_vector_store",
                      return_value=mock_services["vector_store"]):
                with patch("backend.api.v1.chat.get_embeddings_service",
                          return_value=mock_services["embeddings_service"]):
                    
                    response = await client.post(
                        "/api/v1/chat",
                        json={"query": "test query"}
                    )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.json()["detail"].lower()
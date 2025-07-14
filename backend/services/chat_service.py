"""
Chat service for handling Q&A queries using RAG (Retrieval-Augmented Generation).
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .vector_store import VectorStore
from .embeddings import EmbeddingsService
from .llm import LLMService
from ..schemas.chat import ChatResponse, DocumentSource

logger = logging.getLogger(__name__)


class ChatService:
    """Handles chat queries using RAG pattern."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store = VectorStore(db)
        self.embeddings_service = EmbeddingsService()
        self.llm_service = LLMService()
        self.max_context_chunks = 5
        self.similarity_threshold = 0.7
    
    async def process_query(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> ChatResponse:
        """
        Process a chat query using RAG pattern.
        
        Args:
            query: User's question
            chat_history: Previous conversation history
            
        Returns:
            Chat response with answer and sources
        """
        try:
            logger.info(f"Processing query: {query}")
            # Generate embedding for the query
            query_embedding = await self.embeddings_service.generate_embedding(query)
            logger.info(f"Generated embedding for query, shape: {query_embedding.shape}")
            
            # Search for relevant document chunks
            search_results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                k=self.max_context_chunks,
                threshold=self.similarity_threshold
            )
            
            # Format context chunks for LLM
            context_chunks = []
            sources = []
            
            for result in search_results:
                chunk_id, content, similarity, metadata = result
                chunk_data = {
                    "content": content,
                    "metadata": metadata
                }
                context_chunks.append(chunk_data)
                
                # Create source reference
                source = DocumentSource(
                    document_id=metadata.get("document_id", ""),
                    document_name=metadata.get("document_name", "Unknown"),
                    chunk_id=str(chunk_id),
                    similarity_score=similarity
                )
                sources.append(source)
            
            # Generate response using LLM
            response_text = await self.llm_service.generate_response(
                query=query,
                context_chunks=context_chunks,
                chat_history=chat_history
            )
            
            # Remove duplicate sources
            unique_sources = []
            seen_docs = set()
            for source in sources:
                if source.document_id not in seen_docs:
                    unique_sources.append(source)
                    seen_docs.add(source.document_id)
            
            return ChatResponse(
                answer=response_text,
                sources=unique_sources[:3],  # Limit to top 3 sources
                context_used=len(context_chunks) > 0
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            # Return a fallback response
            return ChatResponse(
                answer="I'm sorry, but I encountered an error while processing your query. Please try again or rephrase your question.",
                sources=[],
                context_used=False
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get the health status of all chat service components."""
        try:
            # Check embeddings service
            embeddings_health = await self.embeddings_service.health_check()
            
            # Check LLM service
            llm_health = await self.llm_service.health_check()
            
            # Check vector store
            vector_health = await self.vector_store.health_check()
            
            overall_healthy = all([
                embeddings_health.get("status") == "healthy",
                llm_health.get("status") == "healthy",
                vector_health.get("status") == "healthy"
            ])
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "components": {
                    "embeddings": embeddings_health,
                    "llm": llm_health,
                    "vector_store": vector_health
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "components": {}
            }
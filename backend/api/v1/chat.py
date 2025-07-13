"""
Chat and Q&A API endpoints.
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncpg
import json

from ...schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    SearchRequest,
    SearchResponse,
    SearchResult
)
from ...core.dependencies import (
    get_db,
    get_embeddings_service,
    get_vector_store,
    get_llm_service
)
from ...services import EmbeddingsService, VectorStore, LLMService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: asyncpg.Connection = Depends(get_db),
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Process a chat query and return a response with sources."""
    try:
        # Generate embedding for the query
        query_embedding = await embeddings_service.generate_embedding(request.query)
        
        # Search for relevant chunks
        search_results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            k=request.max_results,
            filter_document_ids=[UUID(id) for id in request.document_ids] if request.document_ids else None,
            threshold=request.similarity_threshold
        )
        
        # Prepare context chunks
        context_chunks = []
        sources = []
        
        for chunk_id, content, similarity, metadata in search_results:
            context_chunks.append({
                "content": content,
                "metadata": metadata
            })
            
            # Get document info for source
            doc_id = metadata.get('document_id')
            if doc_id:
                doc = await db.fetchrow(
                    "SELECT name FROM documents WHERE id = $1",
                    UUID(doc_id)
                )
                if doc and doc['name'] not in sources:
                    sources.append(doc['name'])
        
        # Generate response
        response_text = await llm_service.generate_response(
            query=request.query,
            context_chunks=context_chunks,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            confidence=sum(r[2] for r in search_results) / len(search_results) if search_results else 0.0
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_store: VectorStore = Depends(get_vector_store),
    db: asyncpg.Connection = Depends(get_db)
):
    """Search for relevant document chunks."""
    try:
        # Generate embedding for the query
        query_embedding = await embeddings_service.generate_embedding(request.query)
        
        # Search for relevant chunks
        search_results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            k=request.max_results,
            filter_document_ids=[UUID(id) for id in request.document_ids] if request.document_ids else None,
            threshold=request.similarity_threshold
        )
        
        # Format results
        results = []
        for chunk_id, content, similarity, metadata in search_results:
            # Get document info
            doc_id = metadata.get('document_id')
            doc_name = "Unknown"
            
            if doc_id:
                doc = await db.fetchrow(
                    "SELECT name FROM documents WHERE id = $1",
                    UUID(doc_id)
                )
                if doc:
                    doc_name = doc['name']
            
            results.append(SearchResult(
                chunk_id=str(chunk_id),
                document_id=doc_id,
                document_name=doc_name,
                content=content,
                similarity_score=similarity,
                metadata=metadata
            ))
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search documents: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service)
):
    """Stream chat responses as they're generated."""
    try:
        # Generate embedding and search (same as regular chat)
        query_embedding = await embeddings_service.generate_embedding(request.query)
        
        search_results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            k=request.max_results,
            filter_document_ids=[UUID(id) for id in request.document_ids] if request.document_ids else None,
            threshold=request.similarity_threshold
        )
        
        # Prepare context
        context_chunks = [
            {"content": content, "metadata": metadata}
            for _, content, _, metadata in search_results
        ]
        
        # Generate streaming response
        async def generate():
            async for chunk in llm_service.generate_response(
                query=request.query,
                context_chunks=context_chunks,
                chat_history=request.chat_history,
                stream=True
            ):
                # Send as Server-Sent Events format
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            
            # Send final message with sources
            sources = list(set(
                m.get('document_name', 'Unknown')
                for _, _, _, m in search_results
            ))
            yield f"data: {json.dumps({'sources': sources, 'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Stream chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stream chat response: {str(e)}"
        )


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_store: VectorStore = Depends(get_vector_store),
    llm_service: LLMService = Depends(get_llm_service)
):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            if data.get('type') == 'ping':
                await websocket.send_json({"type": "pong"})
                continue
            
            query = data.get('query', '')
            chat_history = data.get('chat_history', [])
            
            # Process query
            try:
                # Generate embedding and search
                query_embedding = await embeddings_service.generate_embedding(query)
                
                search_results = await vector_store.similarity_search(
                    query_embedding=query_embedding,
                    k=5
                )
                
                # Prepare context
                context_chunks = [
                    {"content": content, "metadata": metadata}
                    for _, content, _, metadata in search_results
                ]
                
                # Stream response
                async for chunk in llm_service.generate_response(
                    query=query,
                    context_chunks=context_chunks,
                    chat_history=chat_history,
                    stream=True
                ):
                    await websocket.send_json({
                        "type": "text",
                        "text": chunk
                    })
                
                # Send sources
                sources = list(set(
                    m.get('document_name', 'Unknown')
                    for _, _, _, m in search_results
                ))
                
                await websocket.send_json({
                    "type": "complete",
                    "sources": sources
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "error": str(e)
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()
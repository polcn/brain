"""
Vector store service implementation using PostgreSQL with pgvector.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from uuid import UUID
import asyncpg
from pgvector.asyncpg import register_vector

from ..core.config import settings
from ..models.chunk import Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Handles vector storage and similarity search using PostgreSQL with pgvector."""
    
    def __init__(self, pool: Optional[asyncpg.Pool] = None):
        self.pool = pool
        self._registered = False
    
    async def initialize(self) -> None:
        """Initialize the vector store and register pgvector extension."""
        if not self.pool:
            raise RuntimeError("Database pool not set")
        
        if not self._registered:
            # Register pgvector extension with asyncpg
            async with self.pool.acquire() as conn:
                await register_vector(conn)
            self._registered = True
            logger.info("pgvector extension registered")
    
    async def upsert_vectors(
        self,
        document_id: UUID,
        chunks: List[str],
        embeddings: List[np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[UUID]:
        """
        Store document chunks with their embeddings.
        
        Args:
            document_id: UUID of the parent document
            chunks: List of text chunks
            embeddings: List of embedding vectors (1536 dimensions)
            metadata: Optional metadata for all chunks
            
        Returns:
            List of chunk IDs created
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        chunk_ids = []
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Delete existing chunks for this document (if re-processing)
                await conn.execute(
                    "DELETE FROM chunks WHERE document_id = $1",
                    document_id
                )
                
                # Insert new chunks
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    # Ensure embedding is numpy array with correct shape
                    if isinstance(embedding, list):
                        embedding = np.array(embedding)
                    
                    if embedding.shape != (1536,):
                        raise ValueError(f"Embedding must have 1536 dimensions, got {embedding.shape}")
                    
                    # Insert chunk with embedding
                    chunk_id = await conn.fetchval(
                        """
                        INSERT INTO chunks (document_id, chunk_index, content, embedding, metadata)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING id
                        """,
                        document_id,
                        i,
                        chunk,
                        embedding.tolist(),  # pgvector expects list, not numpy array
                        json.dumps(metadata) if metadata else None
                    )
                    chunk_ids.append(chunk_id)
                
                logger.info(f"Inserted {len(chunk_ids)} chunks for document {document_id}")
        
        return chunk_ids
    
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter_document_ids: Optional[List[UUID]] = None,
        threshold: Optional[float] = None
    ) -> List[Tuple[UUID, str, float, Dict[str, Any]]]:
        """
        Perform similarity search for the query embedding.
        
        Args:
            query_embedding: Query vector (1536 dimensions)
            k: Number of results to return
            filter_document_ids: Optional list of document IDs to filter by
            threshold: Optional similarity threshold (0-1, higher is more similar)
            
        Returns:
            List of tuples: (chunk_id, content, similarity_score, metadata)
        """
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding)
        
        if query_embedding.shape != (1536,):
            raise ValueError(f"Query embedding must have 1536 dimensions, got {query_embedding.shape}")
        
        # Build query with optional filters
        query = """
            SELECT 
                c.id,
                c.content,
                1 - (c.embedding <=> $1) as similarity,
                c.metadata,
                c.document_id
            FROM chunks c
            WHERE 1=1
        """
        
        params = [query_embedding.tolist()]
        param_count = 1
        
        if filter_document_ids:
            param_count += 1
            query += f" AND c.document_id = ANY(${param_count})"
            params.append(filter_document_ids)
        
        if threshold is not None:
            param_count += 1
            query += f" AND 1 - (c.embedding <=> $1) >= ${param_count}"
            params.append(threshold)
        
        query += f"""
            ORDER BY c.embedding <=> $1
            LIMIT ${param_count + 1}
        """
        params.append(k)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            results = []
            for row in rows:
                results.append((
                    row['id'],
                    row['content'],
                    row['similarity'],
                    {
                        **(json.loads(row['metadata']) if row['metadata'] else {}),
                        'document_id': str(row['document_id'])
                    }
                ))
            
            logger.info(f"Found {len(results)} similar chunks")
            return results
    
    async def get_document_chunks(
        self,
        document_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            List of chunk data dictionaries
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    id, chunk_index, content, chunk_metadata, created_at
                FROM chunks
                WHERE document_id = $1
                ORDER BY chunk_index
                """,
                document_id
            )
            
            return [dict(row) for row in rows]
    
    async def delete_document_vectors(self, document_id: UUID) -> int:
        """
        Delete all vectors for a specific document.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Number of chunks deleted
        """
        async with self.pool.acquire() as conn:
            count = await conn.fetchval(
                "DELETE FROM chunks WHERE document_id = $1 RETURNING COUNT(*)",
                document_id
            )
            logger.info(f"Deleted {count} chunks for document {document_id}")
            return count
    
    async def update_chunk_metadata(
        self,
        chunk_id: UUID,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update metadata for a specific chunk.
        
        Args:
            chunk_id: UUID of the chunk
            metadata: New metadata to merge with existing
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE chunks 
                SET chunk_metadata = COALESCE(chunk_metadata, '{}'::jsonb) || $2
                WHERE id = $1
                """,
                chunk_id,
                metadata
            )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(DISTINCT document_id) as document_count,
                    COUNT(*) as chunk_count,
                    AVG(length(content)) as avg_chunk_length,
                    MAX(created_at) as last_indexed
                FROM chunks
                """
            )
            
            # Check index stats
            index_info = await conn.fetch(
                """
                SELECT 
                    indexname,
                    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
                FROM pg_indexes
                WHERE tablename = 'chunks' AND indexname LIKE '%embedding%'
                """
            )
            
            return {
                "document_count": stats['document_count'] or 0,
                "chunk_count": stats['chunk_count'] or 0,
                "avg_chunk_length": float(stats['avg_chunk_length'] or 0),
                "last_indexed": stats['last_indexed'],
                "indexes": [dict(row) for row in index_info]
            }
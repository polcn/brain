"""
Tests for vector store service.
"""

import pytest
import numpy as np
from uuid import uuid4
from typing import List, Tuple

from backend.services.vector_store import VectorStoreService


@pytest.mark.asyncio
class TestVectorStoreService:
    """Test vector store service functionality."""
    
    async def test_upsert_vectors(self, db_pool, clean_db):
        """Test upserting vectors."""
        service = VectorStoreService(db_pool)
        
        # Prepare test data
        doc_id = uuid4()
        vectors = [
            (uuid4(), np.random.rand(1536), {"content": "test1", "index": 0}),
            (uuid4(), np.random.rand(1536), {"content": "test2", "index": 1}),
        ]
        
        # Upsert vectors
        success = await service.upsert_vectors(doc_id, vectors)
        assert success is True
        
        # Verify vectors were inserted
        async with db_pool.acquire() as conn:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM chunks WHERE document_id = $1",
                doc_id
            )
            assert count == 2
    
    async def test_similarity_search(self, db_pool, clean_db):
        """Test similarity search."""
        service = VectorStoreService(db_pool)
        
        # Insert test vectors
        doc_id = uuid4()
        base_vector = np.random.rand(1536)
        base_vector = base_vector / np.linalg.norm(base_vector)  # Normalize
        
        vectors = [
            (uuid4(), base_vector, {"content": "exact match", "index": 0}),
            (uuid4(), base_vector + np.random.rand(1536) * 0.1, {"content": "similar", "index": 1}),
            (uuid4(), np.random.rand(1536), {"content": "different", "index": 2}),
        ]
        
        await service.upsert_vectors(doc_id, vectors)
        
        # Search for similar vectors
        results = await service.similarity_search(base_vector, k=2)
        
        assert len(results) == 2
        assert results[0][1] == "exact match"  # Content
        assert results[0][2] > 0.9  # High similarity score
    
    async def test_similarity_search_with_filter(self, db_pool, clean_db):
        """Test similarity search with document filter."""
        service = VectorStoreService(db_pool)
        
        # Insert vectors for multiple documents
        doc1_id = uuid4()
        doc2_id = uuid4()
        query_vector = np.random.rand(1536)
        
        await service.upsert_vectors(doc1_id, [
            (uuid4(), query_vector, {"content": "doc1 content", "index": 0}),
        ])
        
        await service.upsert_vectors(doc2_id, [
            (uuid4(), query_vector, {"content": "doc2 content", "index": 0}),
        ])
        
        # Search with filter
        results = await service.similarity_search(
            query_vector,
            k=5,
            filter_document_ids=[doc1_id]
        )
        
        assert len(results) == 1
        assert results[0][1] == "doc1 content"
    
    async def test_similarity_search_with_threshold(self, db_pool, clean_db):
        """Test similarity search with threshold."""
        service = VectorStoreService(db_pool)
        
        # Insert vectors with varying similarity
        doc_id = uuid4()
        base_vector = np.random.rand(1536)
        base_vector = base_vector / np.linalg.norm(base_vector)
        
        # Create vectors with different similarities
        similar_vector = base_vector + np.random.rand(1536) * 0.05
        similar_vector = similar_vector / np.linalg.norm(similar_vector)
        
        different_vector = np.random.rand(1536)
        different_vector = different_vector / np.linalg.norm(different_vector)
        
        vectors = [
            (uuid4(), base_vector, {"content": "exact", "index": 0}),
            (uuid4(), similar_vector, {"content": "similar", "index": 1}),
            (uuid4(), different_vector, {"content": "different", "index": 2}),
        ]
        
        await service.upsert_vectors(doc_id, vectors)
        
        # Search with high threshold
        results = await service.similarity_search(
            base_vector,
            k=10,
            threshold=0.8
        )
        
        # Should only return highly similar vectors
        assert len(results) <= 2
        for result in results:
            assert result[2] >= 0.8  # Similarity score
    
    async def test_get_document_chunks(self, db_pool, clean_db):
        """Test retrieving document chunks."""
        service = VectorStoreService(db_pool)
        
        # Insert chunks
        doc_id = uuid4()
        vectors = [
            (uuid4(), np.random.rand(1536), {"content": f"chunk {i}", "index": i})
            for i in range(5)
        ]
        
        await service.upsert_vectors(doc_id, vectors)
        
        # Get chunks
        chunks = await service.get_document_chunks(doc_id)
        
        assert len(chunks) == 5
        # Verify chunks are ordered by index
        for i, chunk in enumerate(chunks):
            assert chunk["metadata"]["index"] == i
    
    async def test_delete_document_vectors(self, db_pool, clean_db):
        """Test deleting document vectors."""
        service = VectorStoreService(db_pool)
        
        # Insert vectors
        doc_id = uuid4()
        vectors = [
            (uuid4(), np.random.rand(1536), {"content": "test", "index": 0}),
        ]
        
        await service.upsert_vectors(doc_id, vectors)
        
        # Delete vectors
        deleted = await service.delete_document_vectors(doc_id)
        assert deleted == 1
        
        # Verify deletion
        chunks = await service.get_document_chunks(doc_id)
        assert len(chunks) == 0
    
    async def test_get_index_stats(self, db_pool, clean_db):
        """Test getting index statistics."""
        service = VectorStoreService(db_pool)
        
        # Insert vectors for multiple documents
        for i in range(3):
            doc_id = uuid4()
            vectors = [
                (uuid4(), np.random.rand(1536), {"content": f"doc{i}", "index": 0}),
            ]
            await service.upsert_vectors(doc_id, vectors)
        
        # Get stats
        stats = await service.get_index_stats()
        
        assert stats["total_vectors"] == 3
        assert stats["total_documents"] == 3
        assert stats["index_size"] > 0
        assert "vector_dimensions" in stats
    
    async def test_empty_search(self, db_pool, clean_db):
        """Test search with no results."""
        service = VectorStoreService(db_pool)
        
        query_vector = np.random.rand(1536)
        results = await service.similarity_search(query_vector, k=5)
        
        assert len(results) == 0
    
    async def test_vector_normalization(self, db_pool, clean_db):
        """Test that vectors are properly normalized."""
        service = VectorStoreService(db_pool)
        
        # Insert unnormalized vector
        doc_id = uuid4()
        vector = np.array([3.0, 4.0] + [0.0] * 1534)  # Simple 3-4-5 triangle
        vectors = [(uuid4(), vector, {"content": "test", "index": 0})]
        
        await service.upsert_vectors(doc_id, vectors)
        
        # Retrieve and check normalization
        async with db_pool.acquire() as conn:
            stored_vector = await conn.fetchval(
                "SELECT embedding FROM chunks WHERE document_id = $1",
                doc_id
            )
            
            # Convert back to numpy array
            stored_array = np.array(stored_vector)
            
            # Check if normalized (magnitude should be 1)
            magnitude = np.linalg.norm(stored_array)
            assert abs(magnitude - 1.0) < 0.001
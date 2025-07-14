"""
Integration tests for Brain application.
"""

import pytest
import asyncio
from uuid import uuid4
import os
from unittest.mock import patch, Mock, AsyncMock

import asyncpg
import numpy as np

from backend.services.vector_store import VectorStoreService
from backend.services.document_processor import DocumentProcessorService
from backend.core.database import register_vector


@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegration:
    """Integration tests requiring database."""
    
    @pytest.fixture(scope="class")
    async def test_db_pool(self):
        """Create test database pool."""
        # Use test database
        test_db_url = os.getenv("TEST_DATABASE_URL", 
                                "postgresql://brain_user:brain_password@localhost:5433/brain_test")
        
        # Create pool
        pool = await asyncpg.create_pool(
            test_db_url,
            min_size=1,
            max_size=5,
        )
        
        # Register vector extension
        async with pool.acquire() as conn:
            await register_vector(conn)
        
        yield pool
        
        # Cleanup
        await pool.close()
    
    async def test_full_document_processing_pipeline(
        self, 
        test_db_pool, 
        mock_embeddings_service,
        mock_llm_service,
        mock_s3_client,
        sample_txt_content
    ):
        """Test complete document processing pipeline."""
        # Setup services
        vector_store = VectorStoreService(test_db_pool)
        
        # Mock redaction subprocess
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Redacted"
            
            # Create processor
            processor = DocumentProcessorService(
                pool=test_db_pool,
                s3_client=mock_s3_client,
                vector_store=vector_store,
                embeddings_service=mock_embeddings_service,
                llm_service=mock_llm_service
            )
            
            # Process document
            doc_id = uuid4()
            
            # Mock file operations
            with patch.object(processor, "_save_temp_file", 
                            return_value="/tmp/test.txt"):
                with patch("builtins.open", create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = (
                        sample_txt_content.decode()
                    )
                    
                    result = await processor.process_document(
                        sample_txt_content,
                        "test.txt",
                        doc_id,
                        "text/plain"
                    )
        
        # Verify results
        assert result["status"] == "success"
        assert result["chunks_created"] > 0
        
        # Verify chunks in database
        chunks = await vector_store.get_document_chunks(doc_id)
        assert len(chunks) == result["chunks_created"]
        
        # Test similarity search
        query_embedding = np.random.rand(1536)
        results = await vector_store.similarity_search(
            query_embedding,
            k=5,
            filter_document_ids=[doc_id]
        )
        
        assert len(results) > 0
        assert all(chunk[3]["document_id"] == doc_id for chunk in results)
    
    async def test_vector_search_accuracy(self, test_db_pool):
        """Test vector search returns accurate results."""
        vector_store = VectorStoreService(test_db_pool)
        
        # Create known vectors
        base_vector = np.array([1.0, 0.0] + [0.0] * 1534)
        similar_vector = np.array([0.9, 0.1] + [0.0] * 1534)
        different_vector = np.array([0.0, 1.0] + [0.0] * 1534)
        
        # Normalize
        base_vector = base_vector / np.linalg.norm(base_vector)
        similar_vector = similar_vector / np.linalg.norm(similar_vector)
        different_vector = different_vector / np.linalg.norm(different_vector)
        
        # Insert vectors
        doc_id = uuid4()
        vectors = [
            (uuid4(), base_vector, {"content": "exact match", "index": 0}),
            (uuid4(), similar_vector, {"content": "similar", "index": 1}),
            (uuid4(), different_vector, {"content": "different", "index": 2}),
        ]
        
        await vector_store.upsert_vectors(doc_id, vectors)
        
        # Search with base vector
        results = await vector_store.similarity_search(base_vector, k=3)
        
        # Verify order by similarity
        assert results[0][1] == "exact match"
        assert results[1][1] == "similar"
        assert results[2][1] == "different"
        
        # Verify similarity scores are descending
        assert results[0][2] > results[1][2] > results[2][2]
    
    async def test_concurrent_operations(self, test_db_pool):
        """Test concurrent database operations."""
        vector_store = VectorStoreService(test_db_pool)
        
        # Create multiple documents concurrently
        async def create_document(index):
            doc_id = uuid4()
            vectors = [
                (uuid4(), np.random.rand(1536), {"content": f"doc{index}", "index": 0})
            ]
            await vector_store.upsert_vectors(doc_id, vectors)
            return doc_id
        
        # Create 10 documents concurrently
        doc_ids = await asyncio.gather(*[create_document(i) for i in range(10)])
        
        # Verify all were created
        stats = await vector_store.get_index_stats()
        assert stats["total_documents"] >= 10
        
        # Perform concurrent searches
        async def search(query_vector):
            return await vector_store.similarity_search(query_vector, k=5)
        
        query_vectors = [np.random.rand(1536) for _ in range(5)]
        results = await asyncio.gather(*[search(v) for v in query_vectors])
        
        # All searches should complete successfully
        assert all(isinstance(r, list) for r in results)
    
    async def test_transaction_rollback(self, test_db_pool):
        """Test transaction rollback on error."""
        vector_store = VectorStoreService(test_db_pool)
        
        doc_id = uuid4()
        
        # Mock to fail after first insert
        original_execute = test_db_pool.acquire().__aenter__().execute
        call_count = 0
        
        async def failing_execute(query, *args):
            nonlocal call_count
            call_count += 1
            if call_count > 1 and "INSERT INTO chunks" in query:
                raise Exception("Simulated failure")
            return await original_execute(query, *args)
        
        # Try to insert vectors with simulated failure
        with patch.object(test_db_pool, "acquire") as mock_acquire:
            mock_conn = AsyncMock()
            mock_conn.execute = failing_execute
            mock_conn.transaction = AsyncMock()
            
            mock_acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_acquire.return_value.__aexit__ = AsyncMock()
            
            vectors = [
                (uuid4(), np.random.rand(1536), {"content": "test1", "index": 0}),
                (uuid4(), np.random.rand(1536), {"content": "test2", "index": 1}),
            ]
            
            with pytest.raises(Exception):
                await vector_store.upsert_vectors(doc_id, vectors)
        
        # Verify no chunks were inserted
        chunks = await vector_store.get_document_chunks(doc_id)
        assert len(chunks) == 0
    
    async def test_performance_metrics(self, test_db_pool):
        """Test performance of vector operations."""
        vector_store = VectorStoreService(test_db_pool)
        
        # Insert batch of vectors
        doc_id = uuid4()
        vectors = [
            (uuid4(), np.random.rand(1536), {"content": f"chunk {i}", "index": i})
            for i in range(100)
        ]
        
        import time
        
        # Measure insert time
        start = time.time()
        await vector_store.upsert_vectors(doc_id, vectors)
        insert_time = time.time() - start
        
        # Should complete reasonably fast
        assert insert_time < 5.0  # 5 seconds for 100 vectors
        
        # Measure search time
        query_vector = np.random.rand(1536)
        start = time.time()
        results = await vector_store.similarity_search(query_vector, k=10)
        search_time = time.time() - start
        
        # Search should be fast
        assert search_time < 0.5  # 500ms
        assert len(results) == 10
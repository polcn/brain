"""
Pytest configuration and fixtures.
"""

import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import numpy as np
from uuid import uuid4

import asyncpg
from httpx import AsyncClient

from backend.app import app
from backend.core.config import settings
from backend.core.database import get_db_pool
from backend.services.vector_store import VectorStore
from backend.services.embeddings import EmbeddingsService
from backend.services.llm import LLMService
from backend.services.document_processor import DocumentProcessor


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_pool():
    """Create test database pool."""
    pool = await asyncpg.create_pool(
        settings.database_url.replace("/brain", "/brain_test"),
        min_size=1,
        max_size=5,
    )
    yield pool
    await pool.close()


@pytest.fixture
async def clean_db(db_pool):
    """Clean database before each test."""
    async with db_pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE documents, chunks, audit_log CASCADE")
    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_embeddings_service():
    """Mock embeddings service."""
    service = Mock(spec=EmbeddingsService)
    
    # Mock embedding generation
    async def mock_generate_embeddings(texts, normalize=True):
        embeddings = []
        for _ in texts:
            # Generate random 1536-dimensional embedding
            embedding = np.random.rand(1536)
            if normalize:
                embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        return embeddings
    
    service.generate_embeddings = AsyncMock(side_effect=mock_generate_embeddings)
    service.generate_embedding = AsyncMock(
        side_effect=lambda text, normalize=True: mock_generate_embeddings([text], normalize)[0]
    )
    service.estimate_tokens = Mock(return_value=len(texts) * 10 if isinstance(texts, list) else 10)
    service.health_check = AsyncMock(return_value={"status": "healthy", "model": "mock"})
    
    return service


@pytest.fixture
def mock_llm_service():
    """Mock LLM service."""
    service = Mock(spec=LLMService)
    
    # Mock response generation
    async def mock_generate_response(query, context_chunks, chat_history=None, stream=False):
        response = f"Based on the documents, here's information about '{query}'"
        if stream:
            async def stream_response():
                for word in response.split():
                    yield word + " "
            return stream_response()
        return response
    
    service.generate_response = AsyncMock(side_effect=mock_generate_response)
    service.summarize_document = AsyncMock(return_value="This is a mock document summary.")
    service.extract_topics = AsyncMock(return_value=["topic1", "topic2", "topic3"])
    service.health_check = AsyncMock(return_value={"status": "healthy", "model": "mock"})
    
    return service


@pytest.fixture
def mock_s3_client():
    """Mock S3 client."""
    client = Mock()
    client.put_object = AsyncMock()
    client.get_object = AsyncMock(return_value={"Body": AsyncMock(read=AsyncMock(return_value=b"file content"))})
    client.delete_object = AsyncMock()
    return client


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    # This is a minimal valid PDF
    return b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000351 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
445
%%EOF"""


@pytest.fixture
def sample_txt_content():
    """Sample text content for testing."""
    return b"""This is a sample document for testing.
It contains multiple paragraphs with various information.

The document discusses important topics that need to be processed and indexed.
This allows the AI assistant to search and retrieve relevant information.

Each paragraph will be processed as a separate chunk for better retrieval."""


@pytest.fixture
def sample_document():
    """Sample document data."""
    return {
        "id": uuid4(),
        "name": "test_document.pdf",
        "mime_type": "application/pdf",
        "size": 1024,
        "status": "processed",
        "s3_key": f"documents/{uuid4()}/test_document.pdf",
        "original_s3_key": f"originals/{uuid4()}/test_document.pdf",
        "chunk_count": 3,
    }


@pytest.fixture
def sample_chunks():
    """Sample chunk data."""
    doc_id = uuid4()
    return [
        {
            "id": uuid4(),
            "document_id": doc_id,
            "content": "This is the first chunk of text from the document.",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 50,
            "embedding": np.random.rand(1536).tolist(),
            "metadata": {"page": 1},
        },
        {
            "id": uuid4(),
            "document_id": doc_id,
            "content": "This is the second chunk with different information.",
            "chunk_index": 1,
            "start_char": 45,
            "end_char": 95,
            "embedding": np.random.rand(1536).tolist(),
            "metadata": {"page": 1},
        },
        {
            "id": uuid4(),
            "document_id": doc_id,
            "content": "The third chunk contains the conclusion.",
            "chunk_index": 2,
            "start_char": 90,
            "end_char": 130,
            "embedding": np.random.rand(1536).tolist(),
            "metadata": {"page": 2},
        },
    ]
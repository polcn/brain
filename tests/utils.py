"""
Test utilities and helpers.
"""

import asyncio
from typing import Dict, Any, List
from uuid import uuid4
import numpy as np
from datetime import datetime


def create_test_document(
    name: str = "test.pdf",
    status: str = "processed",
    chunk_count: int = 5
) -> Dict[str, Any]:
    """Create a test document dictionary."""
    return {
        "id": uuid4(),
        "name": name,
        "mime_type": "application/pdf" if name.endswith(".pdf") else "text/plain",
        "size": 1024,
        "status": status,
        "s3_key": f"documents/{uuid4()}/{name}",
        "original_s3_key": f"originals/{uuid4()}/{name}",
        "chunk_count": chunk_count,
        "created_at": datetime.utcnow(),
        "processed_at": datetime.utcnow() if status == "processed" else None,
        "error": None
    }


def create_test_chunk(
    document_id: uuid4,
    content: str,
    index: int = 0,
    embedding: np.ndarray = None
) -> Dict[str, Any]:
    """Create a test chunk dictionary."""
    if embedding is None:
        embedding = np.random.rand(1536)
        embedding = embedding / np.linalg.norm(embedding)
    
    return {
        "id": uuid4(),
        "document_id": document_id,
        "content": content,
        "chunk_index": index,
        "start_char": index * 100,
        "end_char": (index + 1) * 100,
        "embedding": embedding.tolist(),
        "metadata": {
            "page": index // 3 + 1,
            "section": f"section_{index}"
        }
    }


def create_test_embeddings(count: int, normalize: bool = True) -> List[np.ndarray]:
    """Create test embeddings."""
    embeddings = []
    for _ in range(count):
        embedding = np.random.rand(1536)
        if normalize:
            embedding = embedding / np.linalg.norm(embedding)
        embeddings.append(embedding)
    return embeddings


async def async_test_timeout(coro, timeout: float = 5.0):
    """Run async test with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise AssertionError(f"Test timed out after {timeout} seconds")


def assert_valid_embedding(embedding: np.ndarray):
    """Assert that an embedding is valid."""
    assert isinstance(embedding, np.ndarray), "Embedding must be numpy array"
    assert embedding.shape == (1536,), f"Embedding must be 1536-dimensional, got {embedding.shape}"
    assert not np.isnan(embedding).any(), "Embedding contains NaN values"
    assert not np.isinf(embedding).any(), "Embedding contains infinite values"


def assert_valid_uuid(value: str):
    """Assert that a string is a valid UUID."""
    try:
        uuid4(value)
    except ValueError:
        raise AssertionError(f"'{value}' is not a valid UUID")


def create_mock_s3_response(content: bytes = b"test content") -> Dict[str, Any]:
    """Create a mock S3 GetObject response."""
    return {
        "Body": type("Body", (), {"read": lambda: content})(),
        "ContentLength": len(content),
        "ContentType": "application/pdf",
        "Metadata": {
            "original_name": "test.pdf"
        }
    }


def create_chat_history(exchanges: int = 2) -> List[Dict[str, str]]:
    """Create test chat history."""
    history = []
    for i in range(exchanges):
        history.extend([
            {"role": "user", "content": f"Question {i+1}"},
            {"role": "assistant", "content": f"Answer to question {i+1}"}
        ])
    return history


class AsyncContextManagerMock:
    """Mock for async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
        self.enter_called = False
        self.exit_called = False
    
    async def __aenter__(self):
        self.enter_called = True
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exit_called = True
        return False
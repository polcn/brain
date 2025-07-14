#!/usr/bin/env python3
"""Test Bedrock directly without going through the Brain app"""

import asyncio
import os
import sys
sys.path.append('/app' if os.path.exists('/app') else '.')

from backend.services.llm import LLMService
from backend.services.embeddings import EmbeddingsService

async def test_bedrock():
    print("Testing Bedrock services directly...")
    
    # Test embeddings
    print("\n1. Testing Embeddings Service:")
    embeddings = EmbeddingsService()
    print(f"   Using mock: {embeddings.use_mock}")
    print(f"   Model: {embeddings.model_id}")
    
    try:
        test_texts = [
            "The Brain Document AI system uses advanced technology",
            "Vector embeddings enable semantic search",
            "Claude Instant provides intelligent responses"
        ]
        
        embeddings_results = await embeddings.generate_embeddings(test_texts)
        print(f"   ✓ Generated {len(embeddings_results)} embeddings")
        print(f"   ✓ Embedding shape: {embeddings_results[0].shape}")
        print(f"   ✓ Sample values: {embeddings_results[0][:5]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test LLM
    print("\n2. Testing LLM Service:")
    llm = LLMService()
    print(f"   Using mock: {llm.use_mock}")
    print(f"   Model: {llm.model_id}")
    
    try:
        # Test with context
        context_chunks = [
            {
                'content': 'The Brain Document AI system has four key features: document redaction, vector embeddings, intelligent Q&A, and PostgreSQL with pgvector.',
                'metadata': {'document_name': 'test-document.txt'}
            }
        ]
        
        response = await llm.generate_response(
            "What are the key features of Brain?",
            context_chunks,
            None,
            False
        )
        
        print(f"   ✓ Generated response ({len(response)} chars)")
        print(f"   ✓ Response preview: {response[:100]}...")
        
        # Test summarization
        summary = await llm.summarize_document(
            ["This is a test document.", "It contains multiple chunks.", "Used for testing."],
            max_length=50
        )
        print(f"   ✓ Summary: {summary[:100]}...")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n3. Testing Health Checks:")
    emb_health = await embeddings.health_check()
    llm_health = await llm.health_check()
    
    print(f"   Embeddings: {emb_health['status']} (mock: {emb_health['using_mock']})")
    print(f"   LLM: {llm_health['status']} (mock: {llm_health['using_mock']})")

if __name__ == "__main__":
    asyncio.run(test_bedrock())
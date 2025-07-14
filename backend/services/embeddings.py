"""
Embeddings service for generating text embeddings using Amazon Bedrock or mock implementation.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import boto3
from botocore.exceptions import ClientError
import hashlib

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Handles text embedding generation using Amazon Bedrock Titan model or mock implementation."""
    
    def __init__(self):
        self.use_mock = False
        try:
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            self.model_id = settings.bedrock_embedding_model
            self.max_batch_size = 25  # Titan supports batches up to 25
            self.max_text_length = 8192  # Titan max input length
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock client: {e}. Using mock embeddings.")
            self.use_mock = True
            self.model_id = "mock-embeddings"
            self.max_batch_size = 100
            self.max_text_length = 8192
    
    async def generate_embedding(
        self,
        text: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            normalize: Whether to normalize the embedding vector
            
        Returns:
            Embedding vector of shape (1536,)
        """
        embeddings = await self.generate_embeddings([text], normalize)
        return embeddings[0]
    
    async def generate_embeddings(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            normalize: Whether to normalize the embedding vectors
            
        Returns:
            List of embedding vectors, each of shape (1536,)
        """
        if not texts:
            return []
        
        # Use mock implementation if Bedrock is not available
        if self.use_mock:
            return await self._generate_mock_embeddings(texts, normalize)
        
        # Truncate texts that are too long
        processed_texts = []
        for text in texts:
            if len(text) > self.max_text_length:
                logger.warning(f"Truncating text from {len(text)} to {self.max_text_length} characters")
                text = text[:self.max_text_length]
            processed_texts.append(text)
        
        # Process in batches
        all_embeddings = []
        for i in range(0, len(processed_texts), self.max_batch_size):
            batch = processed_texts[i:i + self.max_batch_size]
            try:
                batch_embeddings = await self._generate_batch(batch, normalize)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Bedrock embedding failed: {e}. Falling back to mock embeddings.")
                self.use_mock = True
                return await self._generate_mock_embeddings(texts, normalize)
        
        return all_embeddings
    
    async def _generate_batch(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self._call_bedrock,
                texts,
                normalize
            )
            return embeddings
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Bedrock API error: {error_code} - {e.response['Error']['Message']}")
            
            if error_code == 'ThrottlingException':
                # Retry with exponential backoff
                await asyncio.sleep(2)
                return await self._generate_batch(texts, normalize)
            
            raise
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def _call_bedrock(
        self,
        texts: List[str],
        normalize: bool
    ) -> List[np.ndarray]:
        """Make synchronous call to Bedrock API."""
        embeddings = []
        
        # Titan expects one text at a time
        for text in texts:
            request_body = {
                "inputText": text,
                "dimensions": 1536,  # Explicitly request 1536 dimensions
                "normalize": normalize
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            embedding = np.array(response_body['embedding'])
            
            # Verify dimensions
            if embedding.shape != (1536,):
                raise ValueError(f"Expected embedding of shape (1536,), got {embedding.shape}")
            
            embeddings.append(embedding)
        
        return embeddings
    
    async def _generate_mock_embeddings(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> List[np.ndarray]:
        """Generate mock embeddings for testing/development."""
        embeddings = []
        
        for text in texts:
            # Create deterministic embedding based on text hash
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            
            # Use hash to seed random generator for consistent results
            np.random.seed(int(text_hash[:8], 16))
            
            # Generate random embedding
            embedding = np.random.normal(0, 1, 1536).astype(np.float32)
            
            # Normalize if requested
            if normalize:
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
            
            embeddings.append(embedding)
        
        logger.info(f"Generated {len(embeddings)} mock embeddings")
        return embeddings
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the text.
        Rough approximation for cost estimation.
        """
        # Rough estimate: 1 token ≈ 4 characters for English text
        return len(text) // 4
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the embeddings service is working."""
        try:
            # Try to generate a simple embedding
            test_embedding = await self.generate_embedding("test")
            
            return {
                "status": "healthy",
                "model": self.model_id,
                "embedding_dimensions": test_embedding.shape[0],
                "test_successful": True,
                "using_mock": self.use_mock
            }
            
        except Exception as e:
            logger.error(f"Embeddings health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "model": self.model_id,
                "error": str(e),
                "test_successful": False,
                "using_mock": self.use_mock
            }
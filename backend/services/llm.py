"""
LLM service for chat and question answering using Amazon Bedrock.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
import boto3
from botocore.exceptions import ClientError

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM interactions using Amazon Bedrock Claude model."""
    
    def __init__(self):
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.model_id = settings.bedrock_model_id
        self.max_tokens = 4096
        self.temperature = 0.7
    
    async def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False
    ) -> Union[AsyncGenerator[str, None], str]:
        """
        Generate a response to the query using provided context.
        
        Args:
            query: User's question
            context_chunks: Relevant document chunks with metadata
            chat_history: Previous conversation history
            stream: Whether to stream the response
            
        Returns:
            Generated response (string or async generator for streaming)
        """
        # Build the prompt
        prompt = self._build_prompt(query, context_chunks, chat_history)
        
        if stream:
            return self._stream_response(prompt)
        else:
            return await self._generate_complete(prompt)
    
    def _build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build the prompt for the LLM."""
        prompt_parts = []
        
        # System instruction
        prompt_parts.append(
            "You are a helpful AI assistant that answers questions based on the provided documents. "
            "Always cite your sources by referencing the document names. "
            "If the answer cannot be found in the provided context, say so clearly."
        )
        
        # Add context
        if context_chunks:
            prompt_parts.append("\n\nContext from documents:")
            for i, chunk in enumerate(context_chunks, 1):
                doc_name = chunk.get('metadata', {}).get('document_name', 'Unknown')
                content = chunk.get('content', '')
                prompt_parts.append(f"\n[{i}] From document '{doc_name}':\n{content}")
        
        # Add chat history if available
        if chat_history:
            prompt_parts.append("\n\nPrevious conversation:")
            for msg in chat_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"\n{role.capitalize()}: {content}")
        
        # Add current query
        prompt_parts.append(f"\n\nUser: {query}")
        prompt_parts.append("\n\nAssistant:")
        
        return ''.join(prompt_parts)
    
    async def _generate_complete(self, prompt: str) -> str:
        """Generate a complete response."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._call_bedrock,
                prompt,
                False
            )
            return response
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Bedrock API error: {error_code} - {e.response['Error']['Message']}")
            
            if error_code == 'ThrottlingException':
                # Retry with exponential backoff
                await asyncio.sleep(2)
                return await self._generate_complete(prompt)
            
            raise
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _stream_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream response tokens as they're generated."""
        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Start the streaming request
            response_stream = await loop.run_in_executor(
                None,
                self._call_bedrock,
                prompt,
                True
            )
            
            # Yield tokens as they come
            for chunk in response_stream:
                if chunk:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise
    
    def _call_bedrock(self, prompt: str, stream: bool = False):
        """Make synchronous call to Bedrock API."""
        # Prepare request based on model type
        if "claude" in self.model_id.lower():
            request_body = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": self.max_tokens,
                "temperature": self.temperature,
                "top_p": 0.9,
                "stop_sequences": ["\n\nHuman:"]
            }
        else:
            # Generic format for other models
            request_body = {
                "prompt": prompt,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        
        if stream:
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            # Process streaming response
            for event in response['body']:
                chunk = json.loads(event['chunk']['bytes'])
                if 'completion' in chunk:
                    yield chunk['completion']
                elif 'text' in chunk:
                    yield chunk['text']
        else:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract text based on model response format
            if 'completion' in response_body:
                return response_body['completion']
            elif 'text' in response_body:
                return response_body['text']
            else:
                raise ValueError(f"Unexpected response format: {response_body.keys()}")
    
    async def summarize_document(
        self,
        chunks: List[str],
        max_length: int = 500
    ) -> str:
        """
        Generate a summary of document chunks.
        
        Args:
            chunks: List of document chunks
            max_length: Maximum length of summary in words
            
        Returns:
            Document summary
        """
        # Combine chunks up to a reasonable length
        combined_text = '\n\n'.join(chunks[:10])  # Use first 10 chunks
        
        prompt = f"""Please provide a concise summary of the following document content in no more than {max_length} words:

{combined_text}

Summary:"""
        
        return await self._generate_complete(prompt)
    
    async def extract_topics(
        self,
        text: str,
        num_topics: int = 5
    ) -> List[str]:
        """
        Extract key topics from the text.
        
        Args:
            text: Input text
            num_topics: Number of topics to extract
            
        Returns:
            List of topic strings
        """
        prompt = f"""Extract {num_topics} key topics or themes from the following text. 
Return only the topics as a comma-separated list:

{text}

Topics:"""
        
        response = await self._generate_complete(prompt)
        
        # Parse topics from response
        topics = [t.strip() for t in response.split(',')]
        return topics[:num_topics]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the LLM service is working."""
        try:
            # Try a simple completion
            response = await self._generate_complete("Hello, this is a test. Please respond with 'OK'.")
            
            return {
                "status": "healthy",
                "model": self.model_id,
                "test_successful": bool(response),
                "response_preview": response[:50] if response else None
            }
            
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "model": self.model_id,
                "error": str(e),
                "test_successful": False
            }
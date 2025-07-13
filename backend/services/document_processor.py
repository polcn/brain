"""
Document processing service for handling file uploads and text extraction.
"""
import os
import asyncio
import logging
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import subprocess
import aiofiles
from pathlib import Path
import magic
import boto3
from botocore.exceptions import ClientError

from ..core.config import settings
from .embeddings import EmbeddingsService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles document processing pipeline including redaction, chunking, and embedding."""
    
    SUPPORTED_TYPES = {
        'application/pdf': '.pdf',
        'text/plain': '.txt',
        'text/markdown': '.md',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
    }
    
    def __init__(
        self,
        vector_store: VectorStore,
        embeddings_service: EmbeddingsService
    ):
        self.vector_store = vector_store
        self.embeddings_service = embeddings_service
        self.s3_client = boto3.client(
            's3',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.chunk_size = 1000  # characters
        self.chunk_overlap = 200  # characters
        self.redact_path = "/usr/local/bin/redact"  # Path to polcn/redact tool
    
    async def process_document(
        self,
        file_content: bytes,
        filename: str,
        document_id: UUID,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a document through the full pipeline.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            document_id: UUID of the document record
            mime_type: MIME type of the file
            
        Returns:
            Processing results including chunk count and S3 location
        """
        # Validate file type
        if not mime_type:
            mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: {mime_type}")
        
        temp_dir = tempfile.mkdtemp()
        try:
            # Save original file
            original_path = os.path.join(temp_dir, f"original_{filename}")
            async with aiofiles.open(original_path, 'wb') as f:
                await f.write(file_content)
            
            # Redact sensitive information
            redacted_path = await self._redact_document(original_path, temp_dir)
            
            # Extract text
            text_content = await self._extract_text(redacted_path, mime_type)
            
            # Upload redacted file to S3
            s3_key = await self._upload_to_s3(redacted_path, document_id, filename)
            
            # Chunk the text
            chunks = self._create_chunks(text_content)
            
            # Generate embeddings
            embeddings = await self.embeddings_service.generate_embeddings(chunks)
            
            # Store in vector database
            chunk_ids = await self.vector_store.upsert_vectors(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
                metadata={
                    "document_name": filename,
                    "mime_type": mime_type,
                    "s3_key": s3_key
                }
            )
            
            return {
                "status": "processed",
                "chunk_count": len(chunks),
                "s3_key": s3_key,
                "chunk_ids": [str(cid) for cid in chunk_ids],
                "text_length": len(text_content)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            raise
            
        finally:
            # Clean up temp files
            for file in os.listdir(temp_dir):
                os.unlink(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
    
    async def _redact_document(
        self,
        input_path: str,
        output_dir: str
    ) -> str:
        """Redact sensitive information using polcn/redact tool."""
        output_path = os.path.join(output_dir, "redacted_" + os.path.basename(input_path))
        
        # Check if redact tool exists
        if not os.path.exists(self.redact_path):
            logger.warning("Redact tool not found, skipping redaction")
            return input_path
        
        try:
            # Run redact command
            cmd = [
                self.redact_path,
                "-i", input_path,
                "-o", output_path,
                "--remove-pii",
                "--remove-emails",
                "--remove-phones",
                "--remove-ssn"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Redaction failed: {stderr.decode()}")
                # Fall back to original if redaction fails
                return input_path
            
            logger.info(f"Successfully redacted document: {os.path.basename(input_path)}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error running redact tool: {str(e)}")
            # Fall back to original if redaction fails
            return input_path
    
    async def _extract_text(
        self,
        file_path: str,
        mime_type: str
    ) -> str:
        """Extract text content from various file types."""
        if mime_type == 'text/plain' or mime_type == 'text/markdown':
            # Direct text file
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        
        elif mime_type == 'application/pdf':
            # Use pdftotext for PDF files
            try:
                process = await asyncio.create_subprocess_exec(
                    'pdftotext', '-layout', file_path, '-',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"pdftotext failed: {stderr.decode()}")
                
                return stdout.decode('utf-8', errors='ignore')
                
            except FileNotFoundError:
                logger.warning("pdftotext not found, using fallback extraction")
                # Fallback: basic text extraction (would need a library like PyPDF2)
                return "PDF text extraction not available"
        
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # DOCX files would need python-docx or similar
            logger.warning("DOCX extraction not yet implemented")
            return "DOCX text extraction not available"
        
        else:
            raise ValueError(f"Text extraction not supported for {mime_type}")
    
    def _create_chunks(
        self,
        text: str,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Find the end of the chunk
            end = start + chunk_size
            
            # Try to break at a sentence boundary
            if end < text_length:
                # Look for sentence endings
                for sep in ['. ', '! ', '? ', '\n\n']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep != -1:
                        end = last_sep + len(sep)
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - overlap if end < text_length else text_length
        
        logger.info(f"Created {len(chunks)} chunks from {text_length} characters")
        return chunks
    
    async def _upload_to_s3(
        self,
        file_path: str,
        document_id: UUID,
        original_filename: str
    ) -> str:
        """Upload file to S3 and return the key."""
        # Generate S3 key
        file_extension = Path(original_filename).suffix
        s3_key = f"documents/{document_id}/redacted{file_extension}"
        
        try:
            # Upload file
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.s3_client.put_object,
                settings.s3_bucket_name,
                s3_key,
                file_content,
                {
                    'ContentType': magic.from_file(file_path, mime=True),
                    'Metadata': {
                        'document_id': str(document_id),
                        'original_filename': original_filename,
                        'redacted': 'true'
                    }
                }
            )
            
            logger.info(f"Uploaded document to S3: {s3_key}")
            return s3_key
            
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            raise
    
    async def download_from_s3(
        self,
        s3_key: str
    ) -> bytes:
        """Download a file from S3."""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                self.s3_client.get_object,
                settings.s3_bucket_name,
                s3_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            raise
    
    async def delete_from_s3(
        self,
        s3_key: str
    ) -> None:
        """Delete a file from S3."""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.s3_client.delete_object,
                settings.s3_bucket_name,
                s3_key
            )
            logger.info(f"Deleted from S3: {s3_key}")
            
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {str(e)}")
            raise
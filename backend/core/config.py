"""
Application configuration using Pydantic settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Brain Document AI"
    version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://brain_user:brain_password@localhost:5433/brain"
    
    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "brain-documents"
    
    # Bedrock
    bedrock_model_id: str = "anthropic.claude-instant-v1"
    bedrock_embedding_model: str = "amazon.titan-embed-text-v1"
    
    # Redis (optional)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Document processing
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".pdf", ".txt", ".docx"}
    chunk_size: int = 1000  # characters per chunk
    chunk_overlap: int = 200  # overlap between chunks
    
    # Vector search
    embedding_dimension: int = 1536  # Titan embeddings
    max_search_results: int = 10
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
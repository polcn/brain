"""
Separate configuration for Bedrock services to avoid credential conflicts with MinIO
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class BedrockConfig:
    """Configuration specifically for AWS Bedrock services"""
    
    @staticmethod
    def get_aws_credentials():
        """Get AWS credentials for Bedrock, handling MinIO conflict"""
        logger.info("Getting AWS credentials for Bedrock...")
        
        # Check if we have explicit Bedrock credentials in environment
        bedrock_key = os.getenv('BEDROCK_AWS_ACCESS_KEY_ID')
        bedrock_secret = os.getenv('BEDROCK_AWS_SECRET_ACCESS_KEY')
        
        if bedrock_key and bedrock_secret:
            logger.info(f"Using BEDROCK_AWS credentials: {bedrock_key[:10]}...")
            return {
                'aws_access_key_id': bedrock_key,
                'aws_secret_access_key': bedrock_secret
            }
        
        # If running in Docker with MinIO, credentials might be overridden
        # Try to get from .env file directly
        env_path = '/app/.env'
        if os.path.exists(env_path):
            logger.info(f"Reading credentials from {env_path}")
            credentials = {}
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('AWS_ACCESS_KEY_ID=') and 'minioadmin' not in line:
                        credentials['aws_access_key_id'] = line.split('=', 1)[1].strip('"')
                    elif line.startswith('AWS_SECRET_ACCESS_KEY=') and 'minioadmin' not in line:
                        credentials['aws_secret_access_key'] = line.split('=', 1)[1].strip('"')
            
            if len(credentials) == 2:
                logger.info(f"Found AWS credentials in .env: {credentials['aws_access_key_id'][:10]}...")
                return credentials
            else:
                logger.warning(f"Incomplete credentials in .env: {list(credentials.keys())}")
        
        # Fall back to environment variables (might be MinIO)
        env_key = os.getenv('AWS_ACCESS_KEY_ID')
        env_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        logger.warning(f"Using environment variables (might be MinIO): {env_key[:10] if env_key else 'None'}...")
        return {
            'aws_access_key_id': env_key,
            'aws_secret_access_key': env_secret
        }
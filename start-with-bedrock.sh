#!/bin/bash
# Start Brain with AWS Bedrock configuration

# Load AWS credentials
export AWS_ACCESS_KEY_ID=$(grep aws_access_key_id ~/.aws/credentials | cut -d'=' -f2 | tr -d ' ')
export AWS_SECRET_ACCESS_KEY=$(grep aws_secret_access_key ~/.aws/credentials | cut -d'=' -f2 | tr -d ' ')
export BEDROCK_AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export BEDROCK_AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# Check if credentials are loaded
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Error: AWS credentials not found in ~/.aws/credentials"
    exit 1
fi

echo "Starting Brain with AWS Bedrock..."
echo "AWS credentials loaded from ~/.aws/credentials"
echo "AWS Region: ${AWS_REGION:-us-east-1}"

# Start services
docker compose down
docker compose up -d

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 15

# Test Bedrock connection
echo "Testing Bedrock connection..."
docker compose exec backend python -c "
from backend.services.llm import LLMService
from backend.services.embeddings import EmbeddingsService
import asyncio

async def test():
    llm = LLMService()
    embeddings = EmbeddingsService()
    
    print(f'LLM Service - Using mock: {llm.use_mock}, Model: {llm.model_id}')
    print(f'Embeddings Service - Using mock: {embeddings.use_mock}, Model: {embeddings.model_id}')
    
    # Test embeddings
    try:
        embedding = await embeddings.generate_embedding('test')
        print(f'✓ Embeddings working! Shape: {embedding.shape}')
    except Exception as e:
        print(f'✗ Embeddings error: {e}')
    
    # Test LLM
    try:
        response = await llm.generate_response('Hello', [], None, False)
        print(f'✓ LLM working! Response: {response[:50]}...')
    except Exception as e:
        print(f'✗ LLM error: {e}')

asyncio.run(test())
"

echo ""
echo "Services are running:"
echo "- Frontend: http://localhost:3001"
echo "- API: http://localhost:8001"
echo "- API Docs: http://localhost:8001/docs"
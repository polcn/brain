# Deployment Notes - Brain Document AI

## Overview
This document captures important findings and fixes from the initial deployment of the Brain Document AI system.

## Prerequisites Verified
- ✅ Docker Engine
- ✅ Docker Compose v2 (installed via setup script)
- ✅ AWS Credentials (configured but Bedrock access not available)
- ✅ Minimum 30GB disk space (expanded from 20GB)
- ✅ 8GB RAM (t2.large instance)

## Services Successfully Deployed

### Core Services
1. **PostgreSQL with pgvector** (port 5433)
   - Database: `brain`
   - User: `brain_user` 
   - Password: `brain_password`
   - Vector extension enabled

2. **Redis Cache** (port 6379)
   - Used for caching and session management

3. **MinIO S3-Compatible Storage** (ports 9000/9001)
   - Console: http://localhost:9001
   - Credentials: `minioadmin` / `minioadmin`
   - Bucket: `brain-documents`

4. **Backend API** (port 8001)
   - FastAPI application
   - Endpoints: `/`, `/api/v1/health`, `/api/v1/documents/`

## Critical Fixes Applied

### 1. Database Schema Mismatches
The SQLAlchemy models didn't match the init_db.sql schema. Fixed column mappings:
- `name` → `original_name`
- `mime_type` → `content_type`
- `size` → `file_size`
- Removed references to non-existent columns: `chunk_count`, `processed_at`

### 2. Missing Dependencies
Added to requirements.txt:
- `psycopg2-binary==2.9.9` - Required by Alembic for migrations
- `python-magic==0.4.27` - Required for file type detection

### 3. System Libraries
Added to Dockerfile:
- `libmagic1` - Required by python-magic for file type detection

### 4. S3 Configuration for Local Development
Modified document_processor.py to use MinIO credentials when `S3_ENDPOINT_URL` is set:
```python
if settings.s3_endpoint_url:
    # Use MinIO credentials for local development
    s3_config['aws_access_key_id'] = 'minioadmin'
    s3_config['aws_secret_access_key'] = 'minioadmin'
```

### 5. Docker Compose Command
Removed Alembic migrations from startup command to avoid duplicate table errors.

### 6. MinIO Bucket Creation
Fixed minio-init container command syntax and manually created bucket.

## Known Issues and Limitations

### 1. Bedrock Access
- **Issue**: Document processing fails at embedding generation
- **Error**: `AccessDeniedException` when calling Bedrock
- **Solution**: Need proper AWS Bedrock access or implement mock services

### 2. Document Redaction
- **Issue**: `redact` tool not installed in container
- **Solution**: Need to install polcn/redact or implement alternative

### 3. Frontend Deployment
- **Issue**: Not tested due to initial disk space constraints
- **Solution**: Disk space expanded, ready for testing

### 4. Database Migrations
- **Issue**: Alembic migrations fail on existing tables
- **Solution**: Need to implement proper migration strategy

## Environment Variables Required

```bash
# Database
DATABASE_URL="postgresql://brain_user:brain_password@postgres:5432/brain"
REDIS_URL="redis://redis:6379"

# AWS (for production)
AWS_ACCESS_KEY_ID="your-key"
AWS_SECRET_ACCESS_KEY="your-secret"
AWS_REGION="us-east-1"

# S3/MinIO
S3_BUCKET_NAME="brain-documents"
S3_ENDPOINT_URL="http://minio:9000"  # For local development
USE_LOCAL_STORAGE="true"

# Bedrock
BEDROCK_MODEL_ID="anthropic.claude-instant-v1"
BEDROCK_EMBEDDING_MODEL="amazon.titan-embed-text-v1"
```

## Deployment Commands

### Local Development (with MinIO)
```bash
# Start base services
docker compose up -d postgres redis minio

# Create MinIO bucket
docker exec brain-minio mc alias set minio http://localhost:9000 minioadmin minioadmin
docker exec brain-minio mc mb minio/brain-documents --ignore-existing

# Run backend
docker run -d --name brain-backend --network brain_brain-network -p 8001:8001 \
  [environment variables] \
  brain-backend \
  sh -c "python scripts/wait_for_db.py && uvicorn backend.app:app --host 0.0.0.0 --port 8001"
```

### Production Deployment
- Use real S3 instead of MinIO (remove `S3_ENDPOINT_URL`)
- Use managed PostgreSQL (RDS with pgvector)
- Configure proper Bedrock access
- Implement proper secret management

## API Testing

### Health Check
```bash
curl http://localhost:8001/api/v1/health
# Response: {"status":"healthy","service":"brain-api","version":"0.1.0"}
```

### List Documents
```bash
curl http://localhost:8001/api/v1/documents/
# Response: {"documents":[],"total":0,"skip":0,"limit":10}
```

### Upload Document
```bash
curl -X POST -F "file=@document.txt" http://localhost:8001/api/v1/documents/upload
# Currently fails at embedding generation without Bedrock access
```

## Next Steps

1. **For Local Development**
   - Implement mock embedding service
   - Add document redaction bypass for testing
   - Complete frontend deployment

2. **For Production**
   - Configure Bedrock access
   - Install and configure redact tool
   - Implement proper migration strategy
   - Add authentication/authorization
   - Configure HTTPS/SSL
   - Set up monitoring and logging

## Disk Space Requirements

Minimum recommended: 30GB
- Docker images: ~10GB
- PostgreSQL data: ~2GB
- MinIO storage: Variable based on documents
- System and logs: ~5GB
- Buffer: ~13GB
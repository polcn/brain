# REQUIREMENTS.md - Brain (Document AI Assistant)

## Project Overview

Build a Proof of Concept (POC) for **Brain**, a document-based AI assistant that combines document redaction, vector search, and LLM capabilities. This POC integrates the existing redact tool (https://github.com/polcn/redact) to preprocess documents before vectorization.

## Development Environment

- **Platform**: AWS EC2 t2.large instance (8GB RAM, 2 vCPUs)
- **OS**: Ubuntu/Amazon Linux
- **Development Tool**: Claude Code
- **Python Version**: 3.9+ (compatible with current environment)
- **Project Name**: brain
- **Ports**: FastAPI (8001), PostgreSQL (5433), Frontend (3001)

## Core Technologies

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL 15+ with pgvector extension
- **LLM Provider**: Amazon Bedrock (Claude Instant + Titan Embeddings)
- **Storage**: AWS S3 for documents, PostgreSQL for all data and vectors
- **Document Processing**: Integration with polcn/redact tool
- **Frontend**: Simple React app (can be minimal for POC)
- **Caching**: Redis (optional for frequent queries)

## Phase 1: POC Requirements (Target: 2-3 weeks)

### 1. Document Processing Pipeline

```python
# Core flow to implement
1. User uploads document (PDF, DOCX, TXT)
2. Redact sensitive information using polcn/redact
3. Extract and clean text
4. Split into intelligent chunks (500-1000 tokens)
5. Generate embeddings using Bedrock Titan (1536 dimensions)
6. Store vectors in PostgreSQL with pgvector
7. Save redacted document in S3
```

### 2. Database Architecture

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    s3_url TEXT NOT NULL,
    file_size_bytes INTEGER,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,
    metadata JSONB
);

-- Chunks table with vector embeddings
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- Titan embeddings dimension
    token_count INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create HNSW index for fast similarity search
CREATE INDEX chunks_embedding_idx ON chunks 
USING hnsw (embedding vector_cosine_ops);

-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);
```

### 3. Project Structure

```
brain/
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── config.py                 # Environment variables
│   ├── models.py                 # Pydantic models
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── redactor.py          # Wrapper for redact tool
│   │   ├── text_extractor.py   # PDF/DOCX text extraction
│   │   └── chunker.py           # Smart text chunking
│   ├── core/
│   │   ├── __init__.py
│   │   ├── embeddings.py        # Bedrock Titan embeddings
│   │   ├── vector_store.py      # Abstract vector store interface
│   │   └── llm.py              # Bedrock Claude integration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── documents.py         # Document upload/management
│   │   ├── chat.py              # Chat/query endpoints
│   │   └── health.py            # Health check endpoints
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── s3.py               # S3 operations
│   │   └── database.py          # PostgreSQL + pgvector operations
│   └── utils/
│       ├── __init__.py
│       ├── auth.py              # Simple JWT auth
│       └── monitoring.py        # Metrics and logging
├── frontend/
│   ├── index.html               # Simple UI
│   ├── app.js                   # Vanilla JS or React
│   └── style.css
├── scripts/
│   ├── setup_database.py        # Initialize PostgreSQL with pgvector
│   ├── test_pipeline.py         # Test document processing
│   ├── seed_data.py             # Load sample documents
│   └── benchmark_vectors.py     # Performance testing
├── tests/
│   ├── test_api.py
│   ├── test_vectors.py
│   └── conftest.py
├── migrations/                   # Alembic database migrations
│   └── alembic.ini
├── docker-compose.yml           # Local development
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

### 4. API Endpoints

```yaml
Documents:
  POST   /api/documents/upload     # Upload and process document
  GET    /api/documents            # List all documents
  GET    /api/documents/{id}       # Get document metadata
  DELETE /api/documents/{id}       # Delete document and vectors

Chat:
  POST   /api/chat                 # Ask question, get answer
  GET    /api/chat/history         # Get chat history (optional)

Health:
  GET    /api/health               # Service health check
  GET    /api/health/dependencies  # Check PostgreSQL, S3, Bedrock
```

### 5. Key Features for POC

#### Must Have:
- [ ] Document upload (PDF, TXT initially)
- [ ] Automatic redaction before processing
- [ ] Text chunking and embedding generation
- [ ] Vector storage in PostgreSQL with pgvector
- [ ] Basic chat interface
- [ ] Source attribution in responses
- [ ] Simple authentication (JWT)
- [ ] Database migrations with Alembic
- [ ] Connection pooling and performance optimization

#### Nice to Have:
- [ ] DOCX support
- [ ] Progress indicators for processing
- [ ] Multiple document selection in chat
- [ ] Export chat history
- [ ] Basic usage metrics

#### Not Needed for POC:
- Complex security (KMS, etc.)
- Multi-tenancy
- Advanced caching
- Payment integration
- User management beyond basic auth

### 6. Environment Variables

```bash
# .env.example
# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=brain-poc-documents

# Database
DATABASE_URL=postgresql://user:password@localhost:5433/brain
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
PGVECTOR_DIMENSION=1536

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-instant-v1
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1

# App
SECRET_KEY=your-secret-key-here
DEBUG=True
MAX_FILE_SIZE_MB=10
APP_NAME=brain
APP_PORT=8001
FRONTEND_PORT=3001

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Security
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
RATE_LIMIT_PER_MINUTE=60
```

### 7. Development Workflow

```bash
# Day 1-2: Setup and Infrastructure
- Set up EC2 environment
- Install PostgreSQL 15+ with pgvector
- Create S3 bucket
- Configure database with proper schemas
- Set up Docker Compose for local development

# Day 3-5: Document Processing
- Integrate redact tool
- Implement text extraction
- Build chunking logic
- Test embedding generation
- Verify pgvector storage and search

# Day 6-8: API Development
- Create FastAPI structure
- Implement upload endpoint
- Build chat endpoint
- Add basic authentication
- Error handling

# Day 9-10: Frontend
- Create simple upload UI
- Build chat interface
- Display results with sources
- Basic styling

# Day 11-12: Testing and Polish
- End-to-end testing
- Performance optimization
- Documentation
- Demo preparation
```

### 8. Sample Code Structure

#### Vector Store Interface
```python
# core/vector_store.py
from typing import Protocol, List, Tuple
from abc import abstractmethod
import numpy as np

class VectorStore(Protocol):
    @abstractmethod
    async def upsert_vectors(
        self, 
        document_id: str,
        chunks: List[str],
        embeddings: List[np.ndarray]
    ) -> None:
        """Store document chunks with their embeddings"""
        pass
    
    @abstractmethod
    async def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        filter_document_ids: List[str] = None
    ) -> List[Tuple[str, str, float]]:
        """Search for similar chunks
        Returns: List of (chunk_id, chunk_text, similarity_score)
        """
        pass

# storage/database.py - PostgreSQL implementation
from core.vector_store import VectorStore
import asyncpg
from pgvector.asyncpg import register_vector

class PostgresVectorStore(VectorStore):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def upsert_vectors(self, document_id, chunks, embeddings):
        async with self.pool.acquire() as conn:
            await register_vector(conn)
            # Batch insert chunks with embeddings
            await conn.executemany(
                """
                INSERT INTO chunks (document_id, chunk_index, content, embedding)
                VALUES ($1, $2, $3, $4)
                """,
                [
                    (document_id, idx, chunk, embedding)
                    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            )
    
    async def search_similar(self, query_embedding, top_k=5, filter_document_ids=None):
        async with self.pool.acquire() as conn:
            await register_vector(conn)
            query = """
                SELECT id, content, 1 - (embedding <=> $1) as similarity
                FROM chunks
                WHERE ($2::uuid[] IS NULL OR document_id = ANY($2))
                ORDER BY embedding <=> $1
                LIMIT $3
            """
            rows = await conn.fetch(query, query_embedding, filter_document_ids, top_k)
            return [(row['id'], row['content'], row['similarity']) for row in rows]
```

#### Document Upload Handler
```python
# api/documents.py
from fastapi import UploadFile, File
from preprocessing.redactor import RedactWrapper
from core.embeddings import EmbeddingGenerator
from storage.database import PostgresVectorStore
from storage.s3 import S3Storage
import asyncpg

async def upload_document(
    file: UploadFile = File(...),
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    vector_store: PostgresVectorStore = Depends(get_vector_store)
):
    async with db_pool.acquire() as conn:
        try:
            # Start transaction
            async with conn.transaction():
                # 1. Create document record
                doc_id = await conn.fetchval(
                    """
                    INSERT INTO documents (original_filename, filename, processing_status)
                    VALUES ($1, $2, 'processing')
                    RETURNING id
                    """,
                    file.filename, f"{doc_id}_{file.filename}"
                )
                
                # 2. Save and redact file
                temp_path = await save_temp_file(file)
                redacted_path = await RedactWrapper().process(temp_path)
                
                # 3. Extract and chunk text
                text = await extract_text(redacted_path)
                chunks = chunk_text(text, max_tokens=500)
                
                # 4. Generate embeddings in batches
                embeddings = await EmbeddingGenerator().embed_chunks(chunks)
                
                # 5. Store vectors
                await vector_store.upsert_vectors(doc_id, chunks, embeddings)
                
                # 6. Upload to S3
                s3_url = await S3Storage().upload_file(redacted_path, doc_id)
                
                # 7. Update document status
                await conn.execute(
                    """
                    UPDATE documents 
                    SET s3_url = $1, processing_status = 'completed'
                    WHERE id = $2
                    """,
                    s3_url, doc_id
                )
                
        except Exception as e:
            # Update status on error
            await conn.execute(
                """
                UPDATE documents 
                SET processing_status = 'failed', processing_error = $1
                WHERE id = $2
                """,
                str(e), doc_id
            )
            raise
    
    return {"doc_id": doc_id, "status": "processed"}
```

#### Chat Handler
```python
# api/chat.py
from fastapi import Depends
from core.embeddings import EmbeddingGenerator
from storage.database import PostgresVectorStore
from core.llm import BedrockLLM
import asyncpg

async def chat(
    query: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    vector_store: PostgresVectorStore = Depends(get_vector_store)
):
    # 1. Generate query embedding
    query_embedding = await EmbeddingGenerator().embed_text(query)
    
    # 2. Search similar chunks
    results = await vector_store.search_similar(
        query_embedding, 
        top_k=5
    )
    
    # 3. Get document metadata for sources
    async with db_pool.acquire() as conn:
        chunk_ids = [r[0] for r in results]
        metadata = await conn.fetch(
            """
            SELECT c.id, c.content, d.filename, d.original_filename
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.id = ANY($1)
            """,
            chunk_ids
        )
    
    # 4. Build context
    context = "\n\n".join([
        f"[Source: {m['filename']}]\n{m['content']}"
        for m in metadata
    ])
    
    # 5. Generate response
    response = await BedrockLLM().generate(
        query=query,
        context=context
    )
    
    # 6. Log to audit table
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO audit_log (action, resource_type, details)
            VALUES ('chat_query', 'chat', $1::jsonb)
            """,
            {"query": query, "chunk_ids": chunk_ids}
        )
    
    # 7. Return with sources
    return {
        "answer": response,
        "sources": [
            {
                "text": m['content'][:200] + "...",
                "filename": m['original_filename'],
                "similarity": r[2]
            }
            for m, r in zip(metadata, results)
        ]
    }
```

### 9. Testing Requirements

```python
# Minimum tests for POC
- Test document upload with small PDF
- Test redaction is working
- Test embedding generation
- Test pgvector storage and retrieval
- Test vector similarity search accuracy
- Test chat endpoint with sample query
- Test error handling for large files
- Test S3 upload/download
- Test database transactions and rollback
- Test connection pooling under load
- Test vector dimension consistency
```

### 10. Success Criteria

- [ ] Successfully process 10+ documents
- [ ] Redaction removes PII (names, emails, SSNs)
- [ ] Chat responses are relevant and cite sources
- [ ] Response time < 3 seconds for queries (including vector search)
- [ ] No memory leaks during extended use
- [ ] Total cost < $50/month (reduced with pgvector)
- [ ] Can handle concurrent uploads
- [ ] Vector similarity search returns relevant results (>0.7 similarity)
- [ ] Database performance remains stable with 1000+ chunks
- [ ] Successful rollback on processing failures

### 11. Deployment Instructions

```bash
# On EC2 t2.large instance

# 1. Clone repository
git clone https://github.com/yourusername/brain.git
cd brain

# 2. Install PostgreSQL 15 with pgvector
sudo yum install -y postgresql15-server postgresql15-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# 3. Install dependencies
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
python scripts/setup_database.py

# 6. Run migrations
alembic upgrade head

# 7. Start server
uvicorn backend.app:app --host 0.0.0.0 --port 8001

# 8. (Optional) Use tmux for persistent sessions
tmux new -s brain
# Run server in tmux session
```

### 12. Quick Commands

```bash
# Common commands for development

# Start brain
cd ~/brain && source venv/bin/activate && uvicorn backend.app:app --reload

# Test upload
curl -X POST -F "file=@test.pdf" http://localhost:8001/api/documents/upload

# Test chat
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?"}' \
  http://localhost:8001/api/chat

# Connect to database
psql postgresql://user:password@localhost:5433/brain

# Check vector extension
psql -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Monitor vector search performance
psql -c "EXPLAIN ANALYZE SELECT * FROM chunks ORDER BY embedding <=> '[...]' LIMIT 5;"

# Check logs
tail -f brain.log

# Monitor resources
htop  # Check CPU/Memory usage
```

## Cost Management

- Set Bedrock spending limits
- Monitor daily usage via CloudWatch
- Use caching for repeated queries (Redis)
- Implement rate limiting
- Schedule EC2 stop/start for non-work hours
- PostgreSQL instead of Pinecone saves ~$70/month
- Monitor database storage growth
- Implement chunk deduplication

## Security Notes (Enhanced for POC)

- Use environment variables for secrets
- Basic JWT for authentication with rotation
- HTTPS only (use Let's Encrypt)
- Sanitize file uploads with type validation
- Limit file sizes (configurable)
- No public S3 access
- SQL injection prevention with parameterized queries
- Database encryption at rest
- Audit logging for all document access
- Rate limiting per IP/user
- Input validation on all endpoints

## Next Steps After POC

If POC is successful:
1. Add more document types (Excel, Images with OCR)
2. Implement user management and RBAC
3. Add conversation memory with session management
4. Improve chunking strategies (semantic chunking)
5. Add monitoring/analytics (Prometheus/Grafana)
6. Plan for multi-tenancy with database isolation
7. Consider migration to managed PostgreSQL (RDS)
8. Implement caching layer with Redis
9. Add batch processing for multiple documents
10. Evaluate need for dedicated vector database if scale demands

---

## Quick Reference

```yaml
Project: brain
Repo: github.com/polcn/brain
S3 Bucket: brain-poc-documents
Database: PostgreSQL with pgvector
Database Port: 5433
API Port: 8001
Frontend Port: 3001
Vector Dimensions: 1536 (Titan embeddings)
```

## Performance Considerations

### Vector Search Optimization
- Use HNSW index for fast approximate nearest neighbor search
- Tune `m` and `ef_construction` parameters for your use case
- Consider IVFFlat for very large datasets (millions of vectors)
- Monitor query performance with `EXPLAIN ANALYZE`

### Database Connection Pooling
```python
# Recommended pool settings for t2.large
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=5,
    max_size=20,
    max_queries=50000,
    max_inactive_connection_lifetime=300
)
```

### Chunking Strategy
- Target 500-1000 tokens per chunk for optimal context
- Implement sliding window with 10-20% overlap
- Consider semantic boundaries (paragraphs, sections)
- Store chunk metadata for better retrieval

### Caching Strategy
- Cache embeddings for frequently queried documents
- Implement query result caching with TTL
- Use Redis for session management
- Cache S3 presigned URLs
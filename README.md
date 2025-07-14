# Brain - Document AI Assistant

Brain is a document-based AI assistant that combines document redaction, vector search, and LLM capabilities. It processes documents by automatically redacting sensitive information, generating embeddings, and enabling intelligent Q&A through a chat interface.

## Features

- **Automatic Document Redaction**: Integrates with [polcn/redact](https://github.com/polcn/redact) to remove PII before processing
- **Vector Search**: Uses PostgreSQL with pgvector for efficient similarity search
- **LLM Integration**: Powered by Amazon Bedrock (Claude Instant + Titan Embeddings)
- **Source Attribution**: All responses include references to source documents
- **Simple API**: RESTful API built with FastAPI
- **Secure Storage**: Documents stored in AWS S3 with metadata in PostgreSQL

## Quick Start

### Docker Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/polcn/brain.git
cd brain

# Copy environment variables
cp .env.example .env
# Edit .env with your AWS credentials for Bedrock

# Start all services
make init  # First time setup
make up    # Start services
```

Access the services at:
- API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- pgAdmin: http://localhost:5050 (admin@brain.local/admin)

### Manual Installation

#### Prerequisites

- Python 3.9+
- PostgreSQL 15+ with pgvector extension
- AWS Account (for S3 and Bedrock)
- 8GB RAM minimum

#### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/polcn/brain.git
cd brain
```

2. Create virtual environment:
```bash
python3.9 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Initialize database:
```bash
# Install PostgreSQL with pgvector
sudo yum install -y postgresql15-server postgresql15-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql

# Run setup
python scripts/setup_database.py
alembic upgrade head
```

6. Start the server:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8001
```

## API Usage

### Upload Document
```bash
curl -X POST -F "file=@document.pdf" \
  http://localhost:8001/api/v1/documents/upload
```

### Query Documents
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is the main topic of the documents?"}' \
  http://localhost:8001/api/v1/chat
```

### List Documents
```bash
curl http://localhost:8001/api/v1/documents
```

## Project Status

🚧 **POC In Development** - Core backend services implemented, testing and deployment setup in progress.

### Completed
- ✅ FastAPI backend structure
- ✅ Database models (PostgreSQL + pgvector)
- ✅ API endpoints (v1 fully functional)
- ✅ Alembic migration setup
- ✅ Development environment
- ✅ Vector store service (pgvector integration)
- ✅ Embeddings service (Bedrock Titan)
- ✅ LLM service (Bedrock Claude)
- ✅ Document processing pipeline
- ✅ File redaction integration
- ✅ S3 storage integration
- ✅ Unit and integration tests
- ✅ Docker Compose setup

### In Progress
- 🔄 Frontend React application
- 🔄 JWT Authentication implementation
- 🔄 Production deployment setup

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   FastAPI    │────▶│ PostgreSQL  │
│   (React)   │     │   Backend    │     │ + pgvector  │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────┴───────┐
                    │              │
              ┌─────▼────┐  ┌─────▼────┐
              │ Bedrock  │  │   AWS    │
              │   LLM    │  │    S3    │
              └──────────┘  └──────────┘
```

For detailed architecture diagrams, see:
- [Infrastructure Architecture](docs/architecture-diagram.drawio) - Full infrastructure layout
- [Document Processing Flow](docs/document-flow-diagram.drawio) - Document pipeline details

## Configuration

Key environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `AWS_ACCESS_KEY_ID`: AWS credentials for S3 and Bedrock
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: Bucket for storing redacted documents
- `BEDROCK_MODEL_ID`: LLM model (default: anthropic.claude-instant-v1)
- `BEDROCK_EMBEDDING_MODEL`: Embedding model (default: amazon.titan-embed-text-v1)

## Development

### Running Tests
```bash
# Using Make
make test         # Run all tests
make test-cov     # Run with coverage report

# Using Docker Compose
docker-compose run --rm backend pytest

# Using script
./scripts/run_tests.sh         # All tests
./scripts/run_tests.sh unit    # Unit tests only
./scripts/run_tests.sh coverage # With coverage
```

### Code Formatting
```bash
black backend/
flake8 backend/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Performance

- Vector search typically returns results in <100ms
- Document processing scales with document size (roughly 1-2 seconds per page)
- Supports concurrent uploads and queries
- Connection pooling for database efficiency

## Security

- All documents are redacted before storage using polcn/redact
- Audit logging for all operations
- No public S3 access
- SQL injection prevention through parameterized queries
- Environment-based configuration for secrets
- Docker secrets support for production

**Note**: JWT authentication is planned but not yet implemented. Currently using basic authentication.

## Limitations

This is a POC with the following constraints:
- Basic authentication only (JWT planned)
- Single-tenant design
- Limited to PDF, TXT, and DOCX files
- English language support only
- No real-time collaboration features
- Limited to 10MB file uploads

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

## Acknowledgments

- [polcn/redact](https://github.com/polcn/redact) for document redaction
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- Amazon Bedrock for LLM capabilities
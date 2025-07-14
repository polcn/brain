# Brain - Document AI Assistant

Brain is a document-based AI assistant that combines document redaction, vector search, and LLM capabilities. It processes documents by automatically redacting sensitive information, generating embeddings, and enabling intelligent Q&A through a chat interface.

## Features

- **JWT Authentication**: Secure API access with JSON Web Tokens
- **User Management**: Multi-tenant support with user-scoped documents
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

# Run the automated setup script
./setup.sh
```

The setup script will guide you through:
- Installing Docker Compose if needed
- Creating your configuration
- Starting the services
- Providing access URLs

For manual setup or more options, see [DEPLOYMENT.md](DEPLOYMENT.md).

**Important**: See [DEPLOYMENT_NOTES.md](DEPLOYMENT_NOTES.md) for critical fixes and known issues from initial deployment.

Access the services at:
- **Frontend**: http://localhost:3001
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **pgAdmin**: http://localhost:5050 (admin@brain.local/admin) - optional, use `--profile full`

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

### Authentication

#### Register a new user
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"newuser","password":"securepass123"}' \
  http://localhost:8001/api/v1/auth/register
```

#### Login
```bash
# Returns JWT token
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser&password=securepass123" \
  http://localhost:8001/api/v1/auth/login

# Or with JSON
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"securepass123"}' \
  http://localhost:8001/api/v1/auth/login-json
```

### Using Protected Endpoints

All document operations require authentication. Include the JWT token in the Authorization header:

#### Upload Document
```bash
TOKEN="your-jwt-token"
curl -X POST -F "file=@document.pdf" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/documents/upload
```

#### Query Documents
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"What is the main topic of the documents?"}' \
  http://localhost:8001/api/v1/chat/
```

#### List Documents
```bash
# Lists only documents owned by the authenticated user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/documents
```

## Project Status

🎉 **POC Fully Deployed** - Complete document processing pipeline, chat functionality, and React frontend all working with mock services. Ready for development and demo.

### Completed
- ✅ FastAPI backend structure with full REST API
- ✅ PostgreSQL database with pgvector for similarity search
- ✅ JWT authentication with user management
- ✅ Multi-tenant document isolation
- ✅ React frontend application (Material-UI)
- ✅ Docker Compose development environment
- ✅ MinIO for S3-compatible local storage
- ✅ Document upload and processing pipeline
- ✅ Text extraction from PDF/DOCX/TXT files
- ✅ Document redaction integration (polcn/redact)
- ✅ Mock services for embeddings and LLM
- ✅ Vector similarity search
- ✅ Chat/Q&A with source attribution
- ✅ Health monitoring endpoints
- ✅ Comprehensive test suite
- ✅ API documentation (OpenAPI/Swagger)
- ✅ nginx reverse proxy for frontend

### Current Architecture
- **Frontend**: React + TypeScript + Material-UI on port 3001
- **Backend**: FastAPI + asyncpg on port 8001
- **Database**: PostgreSQL with pgvector on port 5433
- **Cache**: Redis on port 6379
- **Storage**: MinIO (S3-compatible) on ports 9000/9001
- **Auth**: JWT tokens with 30-minute expiration

### Known Issues
- ⚠️ Redaction API returns 403 errors (falls back to unredacted text)
- ⚠️ Frontend lacks login/register UI components (API supports it)
- ✅ Bedrock access configured and working with AWS credentials

### Next Steps
- 🔄 Add authentication UI to frontend
- ✅ Configure production AWS Bedrock access (completed)
- 🔄 Implement proper secret management
- 🔄 Add monitoring and observability

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

- **JWT Authentication**: All API endpoints require valid JWT tokens
- **User Isolation**: Documents are scoped to individual users
- **Password Security**: Bcrypt hashing for secure password storage
- **Document Redaction**: All documents are redacted before storage using polcn/redact
- **Audit Logging**: All operations are logged with user tracking
- **No Public S3 Access**: Secure document storage
- **SQL Injection Prevention**: Parameterized queries throughout
- **Environment-based Configuration**: Secrets management via environment variables
- **Docker Secrets Support**: Production-ready secrets handling

### Default Admin Account
For initial setup, a default admin account is created:
- Username: `admin`
- Password: `admin123`
- **Important**: Change this password immediately in production!

## Limitations

This is a POC with the following constraints:
- Limited to PDF, TXT, and DOCX files
- English language support only
- No real-time collaboration features
- Limited to 10MB file uploads
- Mock services provide simplified responses for demo purposes
- Production deployment requires proper AWS Bedrock access for optimal performance
- Chat endpoint has a minor issue with mock LLM response format
- Redaction API returns 403 errors (falls back to unredacted text)

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
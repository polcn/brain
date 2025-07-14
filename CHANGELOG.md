# Changelog

All notable changes to Brain will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with PostgreSQL + pgvector architecture
- Core document processing pipeline design
- Integration with polcn/redact for PII removal
- Vector similarity search using pgvector
- FastAPI backend structure with modular organization
- Docker Compose for local development
- Comprehensive documentation (README, REQUIREMENTS, CLAUDE, CONTRIBUTING)
- Database models for documents, chunks, and audit logging
- Pydantic schemas for API validation
- Health check endpoints with pgvector verification
- Document upload and management API endpoints
- Chat/Q&A API structure
- Alembic database migration setup
- Claude hooks for completion notifications
- Python virtual environment with all dependencies
- **Vector Store Service** - Complete implementation with pgvector
  - Upsert vectors with metadata
  - Similarity search with filtering
  - Document chunk management
  - Index statistics
- **Embeddings Service** - Amazon Bedrock Titan integration
  - Batch embedding generation
  - 1536-dimensional vectors
  - Token estimation
  - Health check endpoint
- **LLM Service** - Bedrock Claude integration
  - Context-aware responses
  - Streaming support
  - Document summarization
  - Topic extraction
- **Document Processor** - Full pipeline implementation
  - File type validation
  - PII redaction with polcn/redact
  - Text extraction (PDF, TXT)
  - Smart text chunking
  - S3 storage integration
- **Dependency Injection** - Service management
- **API v1 Implementation** - All endpoints functional
- **Comprehensive Test Suite** - Unit and integration tests
  - Service tests with mocking
  - API endpoint tests
  - Integration tests with database
  - Test utilities and fixtures
  - 80% coverage requirement
- **Docker Compose Setup** - Complete local development environment
  - Multi-service orchestration
  - Development and production configurations
  - MinIO for local S3
  - pgAdmin for database management
  - Makefile for easy commands
- **Architecture Documentation** - draw.io diagrams
  - Infrastructure architecture diagram
  - Document processing flow diagram
- **Frontend React Application** - Complete UI implementation
  - Chat interface with real-time responses
  - Document upload with drag-and-drop
  - Document management dashboard
  - Material-UI design system
  - TypeScript and Vite setup
  - Docker containerization

### Changed
- Switched from Pinecone to PostgreSQL + pgvector for vector storage
- Updated Python requirement to 3.9+ for compatibility
- Custom ports configuration (8001, 5433, 3001) to avoid conflicts
- Restructured API routes to use v1 namespace

### Security
- Added comprehensive .gitignore for security
- Implemented audit logging design
- SQL injection prevention patterns
- Document redaction before storage

## [0.1.0] - 2025-01-14

Initial POC release with core functionality:
- Document upload and redaction
- Vector storage with pgvector
- Chat interface with source attribution
- Docker development environment
- Comprehensive test coverage

[Unreleased]: https://github.com/polcn/brain/compare/v0.1.0...HEAD
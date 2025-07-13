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

### Changed
- Switched from Pinecone to PostgreSQL + pgvector for vector storage
- Updated Python requirement to 3.9+ for compatibility
- Custom ports configuration (8001, 5433, 3001) to avoid conflicts

### Security
- Added comprehensive .gitignore for security
- Implemented audit logging design
- SQL injection prevention patterns

## [0.1.0] - TBD

Initial POC release (planned)

[Unreleased]: https://github.com/polcn/brain/compare/v0.1.0...HEAD
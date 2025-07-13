# CLAUDE.md - AI Assistant Instructions for Brain Project

This document provides specific instructions for AI assistants (like Claude) working on the Brain project.

## Project Context

Brain is a document AI assistant POC that:
- Uses PostgreSQL with pgvector (NOT Pinecone) for vector storage
- Runs on AWS EC2 with limited resources (t2.large)
- Integrates with polcn/redact for document sanitization
- Uses Amazon Bedrock for LLM and embeddings

## Important Architectural Decisions

### Database Choice
- **Use PostgreSQL + pgvector** for all vector operations
- **Do NOT use Pinecone** - this was changed to simplify architecture
- Single database approach for both metadata and vectors
- Connection pooling is critical for performance

### Port Configuration
- FastAPI: **8001** (not 8000)
- PostgreSQL: **5433** (not 5432)
- Frontend: **3001** (not 3000)

### Python Version
- Use Python **3.9+** (not 3.11+ as originally specified)
- This matches the EC2 environment setup

## Code Style Guidelines

### Python
- Use type hints for all functions
- Async/await for all I/O operations
- Use dependency injection with FastAPI
- Follow PEP 8 style guide
- Add docstrings to all public functions

### Database Operations
- Always use parameterized queries
- Use connection pooling via asyncpg
- Wrap multi-step operations in transactions
- Handle rollbacks properly

### Error Handling
- Log all errors with context
- Return meaningful error messages to users
- Never expose internal details in API responses
- Always clean up resources (files, connections)

## Common Patterns

### Vector Operations
```python
# Always register vector type
await register_vector(conn)

# Use proper vector syntax
# Good: embedding <=> $1
# Bad: embedding = $1
```

### File Processing
```python
# Always clean up temp files
try:
    temp_path = save_temp_file(file)
    # process file
finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)
```

### Transaction Management
```python
async with conn.transaction():
    # All related operations here
    # Automatic rollback on exception
```

## Testing Requirements

When adding new features:
1. Add unit tests for business logic
2. Add integration tests for API endpoints
3. Test database rollback scenarios
4. Verify vector dimension consistency (1536)
5. Test with actual PDF files

## Performance Considerations

- Batch embedding generation (don't embed one at a time)
- Use EXPLAIN ANALYZE for query optimization
- Monitor connection pool usage
- Cache frequently accessed data
- Use pagination for large result sets

## Security Best Practices

1. **Never log sensitive data** (file contents, PII)
2. **Validate all inputs** before processing
3. **Use prepared statements** for all SQL
4. **Sanitize filenames** before storage
5. **Check file types** before processing
6. **Rate limit API endpoints**

## Common Pitfalls to Avoid

1. **Don't hardcode credentials** - use environment variables
2. **Don't assume file paths** - use os.path.join
3. **Don't forget to close connections** - use context managers
4. **Don't store raw documents** - always redact first
5. **Don't ignore async context** - await all async calls

## Development Workflow

1. Read REQUIREMENTS.md for full context
2. Check existing code patterns before implementing
3. Run tests before committing
4. Update documentation for API changes
5. Consider performance impact of changes

## Database Schema

Key tables to understand:
- `documents`: Document metadata and status
- `chunks`: Text chunks with vector embeddings
- `audit_log`: All system actions for compliance

## Useful Commands

```bash
# Check vector extension
psql -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Monitor query performance
psql -c "EXPLAIN ANALYZE SELECT * FROM chunks ORDER BY embedding <=> '[...]' LIMIT 5;"

# Test vector dimension
psql -c "SELECT pg_typeof(embedding), vector_dims(embedding) FROM chunks LIMIT 1;"
```

## Migration Notes

If migrating from Pinecone to pgvector:
1. Export vectors with metadata
2. Transform to PostgreSQL format
3. Batch insert with proper dimensions
4. Rebuild indexes after bulk load
5. Verify search quality

## Debugging Tips

1. Enable SQL query logging in development
2. Use structlog for consistent log format
3. Monitor memory usage during embedding generation
4. Check S3 permissions if uploads fail
5. Verify Bedrock model access in correct region

## Development Setup

### Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/polcn/brain.git
   cd brain
   ```

2. Set up local development environment:
   ```bash
   # Start Docker services
   docker-compose up -d
   
   # Create virtual environment
   python3.9 -m venv venv
   source venv/bin/activate
   
   # Install all dependencies
   pip install -r requirements-dev.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with appropriate values
   ```

### Git Workflow
- The repository uses GitHub CLI for authentication
- Main branch is protected - work in feature branches
- Commit messages should be descriptive (no emoji or attribution lines)
- Run tests before pushing

### Local Development Commands
```bash
# Run with auto-reload
uvicorn backend.app:app --reload --port 8001

# Run tests
pytest -v

# Format code
black backend/
isort backend/

# Type checking
mypy backend/

# Start all services
docker-compose up
```

## Repository Information

- **GitHub**: https://github.com/polcn/brain
- **Primary Branch**: main
- **Issue Tracking**: GitHub Issues
- **Documentation**: See REQUIREMENTS.md for detailed architecture

## Contact

For architectural decisions or major changes, refer to REQUIREMENTS.md first. This project prioritizes simplicity and cost-effectiveness over scale for the POC phase.
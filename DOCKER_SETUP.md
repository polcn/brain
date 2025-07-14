# Docker Development Setup

This guide explains how to run the Brain application using Docker Compose for local development.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (optional, for using Makefile commands)
- 4GB+ RAM available for Docker

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/polcn/brain.git
   cd brain
   ```

2. **Copy environment variables**:
   ```bash
   cp .env.example .env
   ```

3. **Start all services**:
   ```bash
   make init  # First time setup
   # OR
   docker-compose up
   ```

4. **Access the services**:
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
   - pgAdmin: http://localhost:5050 (admin@brain.local/admin)

## Available Services

### Core Services
- **postgres**: PostgreSQL with pgvector extension
- **redis**: Redis for caching
- **backend**: FastAPI application
- **minio**: Local S3-compatible storage

### Development Tools
- **pgadmin**: Database management UI
- **minio-init**: Automatic bucket creation

### Optional Services
- **frontend**: React application (use `--profile frontend`)
- **test**: Test runner (use `--profile test`)

## Common Commands

### Using Make (Recommended)

```bash
# Start services
make up

# View logs
make logs

# Run tests
make test

# Open shell in backend
make shell

# Stop services
make down

# Clean everything
make clean
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Run tests
docker-compose run --rm backend pytest

# Execute commands
docker-compose exec backend /bin/bash

# Stop services
docker-compose down
```

## Development Workflow

### 1. Making Code Changes

The backend code is mounted as a volume, so changes are reflected immediately with hot-reload enabled.

### 2. Database Migrations

Create a new migration:
```bash
make migrate-create
# OR
docker-compose exec backend alembic revision --autogenerate -m "your message"
```

Apply migrations:
```bash
make migrate
# OR
docker-compose exec backend alembic upgrade head
```

### 3. Running Tests

Run all tests:
```bash
make test
```

Run specific test:
```bash
make test-vector_store  # runs test_vector_store.py
```

Run with coverage:
```bash
make test-cov
```

### 4. Code Quality

Format code:
```bash
make format
```

Run linters:
```bash
make lint
```

Security scan:
```bash
make security
```

## Environment Variables

Key environment variables for local development:

```env
# Database (handled by Docker)
DATABASE_URL=postgresql://brain_user:brain_password@postgres:5432/brain

# MinIO (local S3)
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET_NAME=brain-documents

# For Bedrock, use your AWS credentials
BEDROCK_MODEL_ID=anthropic.claude-instant-v1
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
```

## Troubleshooting

### Port Conflicts

If you get port binding errors:
```bash
# Check what's using the ports
lsof -i :8001  # Backend
lsof -i :5433  # PostgreSQL
lsof -i :6379  # Redis

# Change ports in docker-compose.yml if needed
```

### Database Issues

Reset database:
```bash
docker-compose down -v  # Remove volumes
docker-compose up
```

Check database logs:
```bash
docker-compose logs postgres
```

Connect to database:
```bash
make db-shell
# OR
docker-compose exec postgres psql -U brain_user -d brain
```

### Container Issues

Rebuild containers:
```bash
docker-compose build --no-cache
```

Remove all containers and images:
```bash
docker-compose down
docker system prune -a
```

### Memory Issues

If containers are running out of memory:
1. Increase Docker memory allocation
2. Reduce service replicas
3. Use `docker stats` to monitor usage

## Production Deployment

For production deployment:

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or with Make
make prod
```

Key differences in production:
- No hot-reload
- Gunicorn with multiple workers
- No development tools (pgAdmin, etc.)
- Real AWS services instead of MinIO
- Nginx reverse proxy
- SSL/TLS enabled

## Advanced Usage

### Using Profiles

Run with specific profiles:
```bash
# Include frontend
docker-compose --profile frontend up

# Run tests
docker-compose --profile test run test
```

### Custom Networks

The services use a custom network `brain-network` for inter-service communication.

### Volume Management

Persistent data is stored in named volumes:
- `postgres_data`: Database files
- `redis_data`: Redis persistence
- `minio_data`: Object storage

Back up volumes:
```bash
docker run --rm -v brain_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [MinIO Documentation](https://docs.min.io/)
# Brain Document AI - Deployment Guide

## Quick Start with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- AWS credentials (for Bedrock access)
- At least 4GB of available RAM

#### Installing Docker Compose on Amazon Linux 2023
```bash
# Install Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins/
sudo curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Verify installation
docker compose version
```

Note: On Amazon Linux 2023, use `docker compose` instead of `docker-compose` in all commands.

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/polcn/brain.git
   cd brain
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update:
   - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (required for Bedrock)
   - `AWS_REGION` (ensure Bedrock is available in this region)
   - Other settings as needed

3. **Start the services**
   ```bash
   # Start core services (backend + dependencies)
   docker compose up -d

   # Or start all services including frontend
   docker compose --profile full up -d

   # View logs
   docker compose logs -f
   ```

4. **Access the application**
   - Backend API: http://localhost:8001
   - Frontend: http://localhost:3001 (if using full profile)
   - API Documentation: http://localhost:8001/docs
   - pgAdmin: http://localhost:5050 (if using tools profile)
   - MinIO Console: http://localhost:9001 (username: minioadmin, password: minioadmin)

### Docker Compose Profiles

- **Default**: Core services (PostgreSQL, Redis, MinIO, Backend)
- **frontend**: Includes the React frontend
- **full**: All services including frontend
- **tools**: Includes pgAdmin for database management

Examples:
```bash
# Start with frontend
docker compose --profile frontend up -d

# Start with pgAdmin
docker compose --profile tools up -d

# Start everything
docker compose --profile full --profile tools up -d
```

### Verify Installation

1. Check service health:
   ```bash
   docker compose ps
   ```

2. Test the API:
   ```bash
   curl http://localhost:8001/health
   ```

3. Run initial tests:
   ```bash
   docker compose exec backend pytest
   ```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: Deletes all data)
docker compose down -v
```

## Production Deployment

For production deployment on AWS EC2:

1. **Use real S3 instead of MinIO**:
   - Comment out or remove MinIO services from docker-compose.yml
   - Update `.env` to remove `S3_ENDPOINT_URL`
   - Set `USE_LOCAL_STORAGE=false`

2. **Use managed PostgreSQL (RDS)**:
   - Create RDS instance with pgvector extension
   - Update `DATABASE_URL` in `.env`
   - Remove postgres service from docker-compose.yml

3. **Security considerations**:
   - Use secrets management (AWS Secrets Manager)
   - Enable HTTPS with SSL certificates
   - Set up proper firewall rules
   - Use strong passwords and rotate credentials

4. **Performance tuning**:
   - Adjust PostgreSQL connection pool settings
   - Configure Redis memory limits
   - Set appropriate resource limits in docker-compose.yml

## Troubleshooting

### Database connection issues
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U brain_user -d brain
```

### Backend startup issues
```bash
# Check backend logs
docker compose logs backend

# Run migrations manually
docker compose exec backend alembic upgrade head
```

### MinIO/S3 issues
```bash
# Check MinIO logs
docker compose logs minio

# Access MinIO console
# http://localhost:9001
# Username: minioadmin
# Password: minioadmin
```

### Reset everything
```bash
# Stop services and remove all data
docker compose down -v

# Remove all images
docker compose down --rmi all

# Start fresh
docker compose up -d
```
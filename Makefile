# Makefile for Brain project

.PHONY: help build up down logs shell test clean migrate init dev prod

# Default target
help:
	@echo "Brain Development Commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make shell    - Open shell in backend container"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up volumes and containers"
	@echo "  make migrate  - Run database migrations"
	@echo "  make init     - Initialize project (build, migrate, etc.)"
	@echo "  make dev      - Start development environment"
	@echo "  make prod     - Start production environment"

# Build Docker images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Backend API: http://localhost:8001"
	@echo "MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
	@echo "pgAdmin: http://localhost:5050 (admin@brain.local/admin)"

# Start development environment with logs
dev:
	docker-compose up

# Start production environment
prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# View specific service logs
logs-%:
	docker-compose logs -f $*

# Open shell in backend container
shell:
	docker-compose exec backend /bin/bash

# Open Python shell in backend container
python:
	docker-compose exec backend python

# Run tests
test:
	docker-compose run --rm backend pytest

# Run specific test file
test-%:
	docker-compose run --rm backend pytest tests/test_$*.py

# Run tests with coverage
test-cov:
	docker-compose run --rm backend pytest --cov=backend --cov-report=html

# Run database migrations
migrate:
	docker-compose exec backend alembic upgrade head

# Create new migration
migrate-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend alembic revision --autogenerate -m "$$msg"

# Rollback migration
migrate-rollback:
	docker-compose exec backend alembic downgrade -1

# Clean up everything
clean:
	docker-compose down -v
	docker system prune -f

# Format code
format:
	docker-compose run --rm backend black backend/
	docker-compose run --rm backend isort backend/

# Lint code
lint:
	docker-compose run --rm backend flake8 backend/
	docker-compose run --rm backend mypy backend/

# Security scan
security:
	docker-compose run --rm backend bandit -r backend/

# Initialize project
init: build
	docker-compose up -d postgres redis minio
	sleep 5
	docker-compose run --rm backend alembic upgrade head
	docker-compose up -d
	@echo "Brain project initialized!"

# Database operations
db-shell:
	docker-compose exec postgres psql -U brain_user -d brain

db-backup:
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U brain_user brain > backups/brain_$$(date +%Y%m%d_%H%M%S).sql

db-restore:
	@echo "Available backups:"
	@ls -1 backups/*.sql
	@read -p "Enter backup filename: " file; \
	docker-compose exec -T postgres psql -U brain_user brain < $$file

# MinIO operations
minio-shell:
	docker-compose run --rm minio-init mc config host add minio http://minio:9000 minioadmin minioadmin && \
	docker-compose run --rm minio-init mc ls minio/

# Check service health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8001/health | jq . || echo "Backend not healthy"
	@docker-compose ps

# Development shortcuts
restart:
	docker-compose restart backend

rebuild: down build up

fresh: clean init
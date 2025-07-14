#!/bin/bash
# Brain Document AI - Quick Setup Script

set -e

echo "========================================="
echo "Brain Document AI - Quick Setup"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null 2>&1; then
    echo "Docker Compose not found. Installing Docker Compose plugin..."
    
    # Install Docker Compose plugin
    sudo mkdir -p /usr/local/lib/docker/cli-plugins/
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
    sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    
    echo "Docker Compose installed successfully!"
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your AWS credentials"
    echo "   Required: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Offer to start services
echo ""
echo "Ready to start Brain services!"
echo ""
echo "Choose deployment option:"
echo "1) Backend only (API + dependencies)"
echo "2) Full stack (Backend + Frontend)"
echo "3) Full stack + Tools (includes pgAdmin)"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Starting backend services..."
        docker compose up -d
        ;;
    2)
        echo "Starting full stack..."
        docker compose --profile full up -d
        ;;
    3)
        echo "Starting full stack with tools..."
        docker compose --profile full --profile tools up -d
        ;;
    4)
        echo "Setup complete. You can start services manually with:"
        echo "  docker compose up -d"
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "Service Status:"
docker compose ps

# Display access information
echo ""
echo "========================================="
echo "Brain is starting up!"
echo "========================================="
echo ""
echo "Access points:"
echo "  - API: http://localhost:8001"
echo "  - API Docs: http://localhost:8001/docs"

if [ "$choice" == "2" ] || [ "$choice" == "3" ]; then
    echo "  - Frontend: http://localhost:3001"
fi

if [ "$choice" == "3" ]; then
    echo "  - pgAdmin: http://localhost:5050"
    echo "    Email: admin@brain.local"
    echo "    Password: admin"
fi

echo "  - MinIO Console: http://localhost:9001"
echo "    Username: minioadmin"
echo "    Password: minioadmin"
echo ""
echo "View logs: docker compose logs -f"
echo "Stop services: docker compose down"
echo ""
echo "Setup complete! 🎉"
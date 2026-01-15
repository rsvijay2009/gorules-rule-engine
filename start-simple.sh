#!/bin/bash
# GoRules BRE Platform - Simple Start Script (Linux/Mac)
# Starts only the essential services: Backend, Rule Engine, Rule Editor

set -e

echo "=========================================="
echo "GoRules BRE Platform - Simple Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "✓ Docker found: $(docker --version)"
else
    echo "❌ Docker not found. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose found: $(docker-compose --version)"
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p rules
mkdir -p fact_registry
echo "✓ Directories ready"

# Copy environment file if needed
if [ ! -f .env ]; then
    if [ -f .env.simple ]; then
        echo "Creating .env from .env.simple..."
        cp .env.simple .env
        echo "✓ .env file created"
    fi
fi

echo ""

# Pull images
echo "Pulling Docker images (this may take a few minutes)..."
docker-compose -f docker-compose.simple.yml pull

echo ""

# Start services
echo "Starting services..."
docker-compose -f docker-compose.simple.yml up -d

echo ""

# Wait for services to be healthy
echo "Waiting for services to start (this may take 1-2 minutes)..."
echo ""

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✓ $service_name is ready"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "⚠ $service_name may need more time"
    return 1
}

# Check PostgreSQL
echo "Checking PostgreSQL..."
sleep 5
if docker-compose -f docker-compose.simple.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✓ PostgreSQL is ready"
else
    echo "⚠ PostgreSQL may need more time"
fi

# Check BRE Platform
echo "Checking BRE Platform..."
check_service "BRE Platform" "http://localhost:8000/health"

# Check GoRules Studio
echo "Checking GoRules Studio..."
check_service "GoRules Studio" "http://localhost:3000/"

# Display status
echo ""
echo "=========================================="
echo "Deployment Status"
echo "=========================================="
docker-compose -f docker-compose.simple.yml ps

# Display access information
echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Access your services:"
echo ""
echo "GoRules Studio (Rule Editor):"
echo "  URL: http://localhost:3000"
echo "  Create and edit rules visually"
echo ""
echo "BRE Platform API:"
echo "  URL: http://localhost:8000/docs"
echo "  Interactive API documentation"
echo ""
echo "PostgreSQL Database:"
echo "  Host: localhost:5432"
echo "  Database: bre_platform"
echo "  User: postgres / Password: postgres"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Open GoRules Studio: http://localhost:3000"
echo "2. Create your first rule"
echo "3. Test via BRE Platform API: http://localhost:8000/docs"
echo ""
echo "📖 Documentation: ./SIMPLE_SETUP.md"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.simple.yml logs -f"
echo "  Stop:         docker-compose -f docker-compose.simple.yml down"
echo "  Restart:      docker-compose -f docker-compose.simple.yml restart"
echo "  Clean reset:  docker-compose -f docker-compose.simple.yml down -v"
echo ""

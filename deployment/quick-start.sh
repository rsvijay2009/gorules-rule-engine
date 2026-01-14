#!/bin/bash

# Self-Hosted GoRules Studio - Quick Start Script
# This script sets up the entire platform in one command

set -e  # Exit on error

echo "========================================="
echo "GoRules BRE Platform - Quick Start"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from template...${NC}"
    cp .env.example .env
    
    echo ""
    echo -e "${YELLOW}IMPORTANT: Please edit .env file with your settings:${NC}"
    echo "  - GITHUB_TOKEN (required)"
    echo "  - KEYCLOAK_ADMIN_PASSWORD (recommended)"
    echo "  - Other passwords (recommended)"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Load environment variables
source .env

# Validate required variables
if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" == "ghp_your_github_personal_access_token_here" ]; then
    echo -e "${RED}❌ GITHUB_TOKEN not set in .env file${NC}"
    echo "Please set a valid GitHub Personal Access Token"
    exit 1
fi

echo -e "${GREEN}✓ Configuration validated${NC}"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p nginx/ssl
mkdir -p postgres
mkdir -p keycloak
mkdir -p prometheus
mkdir -p grafana/dashboards
mkdir -p grafana/datasources
echo -e "${GREEN}✓ Directories created${NC}"

# Make postgres init script executable
chmod +x postgres/init-multiple-dbs.sh

# Pull images
echo ""
echo "Pulling Docker images (this may take a few minutes)..."
docker-compose pull

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to start (this may take 2-3 minutes)..."
echo ""

# Function to check service health
check_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s -o /dev/null "$url"; then
            echo -e "${GREEN}✓ $service is ready${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done
    
    echo -e "${RED}❌ $service failed to start${NC}"
    return 1
}

# Check each service
echo "Checking PostgreSQL..."
sleep 10  # Give postgres time to initialize
docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1 && echo -e "${GREEN}✓ PostgreSQL is ready${NC}" || echo -e "${YELLOW}⚠ PostgreSQL may need more time${NC}"

echo "Checking Keycloak..."
check_service "Keycloak" "http://localhost:8080/health" || true

echo "Checking BRE Platform..."
check_service "BRE Platform" "http://localhost:8000/health" || true

echo "Checking GoRules Studio..."
check_service "GoRules Studio" "http://localhost:3000/health" || true

echo "Checking Grafana..."
check_service "Grafana" "http://localhost:3001/api/health" || true

# Display status
echo ""
echo "========================================="
echo "Deployment Status"
echo "========================================="
docker-compose ps

# Display access information
echo ""
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo ""
echo "Access your services:"
echo ""
echo -e "${GREEN}GoRules Studio:${NC}"
echo "  URL: http://localhost:3000"
echo "  Login: admin / admin123"
echo "  (Change password on first login)"
echo ""
echo -e "${GREEN}BRE Platform API:${NC}"
echo "  URL: http://localhost:8000/docs"
echo "  Interactive API documentation"
echo ""
echo -e "${GREEN}Keycloak Admin:${NC}"
echo "  URL: http://localhost:8080"
echo "  Login: admin / ${KEYCLOAK_ADMIN_PASSWORD:-admin123}"
echo ""
echo -e "${GREEN}Grafana Monitoring:${NC}"
echo "  URL: http://localhost:3001"
echo "  Login: admin / ${GRAFANA_PASSWORD:-admin123}"
echo ""
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo "1. Login to GoRules Studio"
echo "2. Create your first rule"
echo "3. Test via BRE Platform API"
echo "4. View metrics in Grafana"
echo ""
echo "📖 Documentation: ./DEPLOYMENT_GUIDE.md"
echo "📖 Rule Editing Guide: ../docs/RULE_EDITING_GUIDE.md"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To restart: docker-compose restart"
echo ""

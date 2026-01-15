# GoRules BRE Platform - Simple Start Script (Windows PowerShell)
# Starts only the essential services: Backend, Rule Engine, Rule Editor

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GoRules BRE Platform - Simple Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop for Windows first." -ForegroundColor Red
    Write-Host "Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose not found. Please install Docker Compose." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
$directories = @(
    "rules",
    "fact_registry"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}
Write-Host "✓ Directories ready" -ForegroundColor Green

# Copy environment file if needed
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.simple") {
        Write-Host "Creating .env from .env.simple..." -ForegroundColor Yellow
        Copy-Item ".env.simple" ".env"
        Write-Host "✓ .env file created" -ForegroundColor Green
    }
}

Write-Host ""

# Pull images
Write-Host "Pulling Docker images (this may take a few minutes)..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml pull

Write-Host ""

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.simple.yml up -d

Write-Host ""

# Wait for services to be healthy
Write-Host "Waiting for services to start (this may take 1-2 minutes)..." -ForegroundColor Yellow
Write-Host ""

# Function to check service health
function Test-ServiceHealth {
    param (
        [string]$ServiceName,
        [string]$Url,
        [int]$MaxAttempts = 30
    )
    
    $attempt = 0
    while ($attempt -lt $MaxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $ServiceName is ready" -ForegroundColor Green
                return $true
            }
        } catch {
            # Service not ready yet
        }
        $attempt++
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
    
    Write-Host "⚠ $ServiceName may need more time" -ForegroundColor Yellow
    return $false
}

# Check PostgreSQL
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    docker-compose -f docker-compose.simple.yml exec -T postgres pg_isready -U postgres | Out-Null
    Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
} catch {
    Write-Host "⚠ PostgreSQL may need more time" -ForegroundColor Yellow
}

# Check BRE Platform
Write-Host "Checking BRE Platform..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "BRE Platform" -Url "http://localhost:8000/health" | Out-Null

# Check GoRules Studio
Write-Host "Checking GoRules Studio..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "GoRules Studio" -Url "http://localhost:3000/" | Out-Null

# Display status
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
docker-compose -f docker-compose.simple.yml ps

# Display access information
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your services:" -ForegroundColor White
Write-Host ""
Write-Host "GoRules Studio (Rule Editor):" -ForegroundColor Green
Write-Host "  URL: http://localhost:3000" -ForegroundColor White
Write-Host "  Create and edit rules visually" -ForegroundColor Gray
Write-Host ""
Write-Host "BRE Platform API:" -ForegroundColor Green
Write-Host "  URL: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Interactive API documentation" -ForegroundColor Gray
Write-Host ""
Write-Host "PostgreSQL Database:" -ForegroundColor Green
Write-Host "  Host: localhost:5432" -ForegroundColor White
Write-Host "  Database: bre_platform" -ForegroundColor White
Write-Host "  User: postgres / Password: postgres" -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "1. Open GoRules Studio: http://localhost:3000" -ForegroundColor White
Write-Host "2. Create your first rule" -ForegroundColor White
Write-Host "3. Test via BRE Platform API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation: .\SIMPLE_SETUP.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs:    docker-compose -f docker-compose.simple.yml logs -f" -ForegroundColor White
Write-Host "  Stop:         docker-compose -f docker-compose.simple.yml down" -ForegroundColor White
Write-Host "  Restart:      docker-compose -f docker-compose.simple.yml restart" -ForegroundColor White
Write-Host "  Clean reset:  docker-compose -f docker-compose.simple.yml down -v" -ForegroundColor White
Write-Host ""

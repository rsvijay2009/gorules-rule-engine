# Self-Hosted GoRules Studio - Quick Start Script (Windows PowerShell)
# This script sets up the entire platform in one command

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "GoRules BRE Platform - Quick Start" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
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

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file with your settings:" -ForegroundColor Yellow
    Write-Host "  - GITHUB_TOKEN (required)" -ForegroundColor White
    Write-Host "  - KEYCLOAK_ADMIN_PASSWORD (recommended)" -ForegroundColor White
    Write-Host "  - Other passwords (recommended)" -ForegroundColor White
    Write-Host ""
    
    # Open .env in default editor
    Write-Host "Opening .env file in notepad..." -ForegroundColor Yellow
    Start-Process notepad ".env"
    
    $continue = Read-Host "Press Enter to continue after editing .env, or Ctrl+C to exit"
}

# Load environment variables from .env
Write-Host "Loading environment variables..." -ForegroundColor Yellow
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

# Validate required variables
$githubToken = [Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "Process")
if ([string]::IsNullOrEmpty($githubToken) -or $githubToken -eq "ghp_your_github_personal_access_token_here") {
    Write-Host "❌ GITHUB_TOKEN not set in .env file" -ForegroundColor Red
    Write-Host "Please set a valid GitHub Personal Access Token" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Configuration validated" -ForegroundColor Green
Write-Host ""

# Create necessary directories
Write-Host "Creating directories..." -ForegroundColor Yellow
$directories = @(
    "nginx\ssl",
    "postgres",
    "keycloak",
    "prometheus",
    "grafana\dashboards",
    "grafana\datasources"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Pull images
Write-Host ""
Write-Host "Pulling Docker images (this may take a few minutes)..." -ForegroundColor Yellow
docker-compose pull

# Start services
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to be healthy
Write-Host ""
Write-Host "Waiting for services to start (this may take 2-3 minutes)..." -ForegroundColor Yellow
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
Start-Sleep -Seconds 10
try {
    docker-compose exec -T postgres pg_isready -U postgres | Out-Null
    Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
} catch {
    Write-Host "⚠ PostgreSQL may need more time" -ForegroundColor Yellow
}

# Check other services
Write-Host "Checking Keycloak..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "Keycloak" -Url "http://localhost:8080/health" | Out-Null

Write-Host "Checking BRE Platform..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "BRE Platform" -Url "http://localhost:8000/health" | Out-Null

Write-Host "Checking GoRules Studio..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "GoRules Studio" -Url "http://localhost:3000/health" | Out-Null

Write-Host "Checking Grafana..." -ForegroundColor Yellow
Test-ServiceHealth -ServiceName "Grafana" -Url "http://localhost:3001/api/health" | Out-Null

# Display status
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
docker-compose ps

# Display access information
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your services:" -ForegroundColor White
Write-Host ""
Write-Host "GoRules Studio:" -ForegroundColor Green
Write-Host "  URL: http://localhost:3000" -ForegroundColor White
Write-Host "  Login: admin / admin123" -ForegroundColor White
Write-Host "  (Change password on first login)" -ForegroundColor Yellow
Write-Host ""
Write-Host "BRE Platform API:" -ForegroundColor Green
Write-Host "  URL: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Interactive API documentation" -ForegroundColor White
Write-Host ""
Write-Host "Keycloak Admin:" -ForegroundColor Green
Write-Host "  URL: http://localhost:8080" -ForegroundColor White
$keycloakPassword = [Environment]::GetEnvironmentVariable("KEYCLOAK_ADMIN_PASSWORD", "Process")
if ([string]::IsNullOrEmpty($keycloakPassword)) { $keycloakPassword = "admin123" }
Write-Host "  Login: admin / $keycloakPassword" -ForegroundColor White
Write-Host ""
Write-Host "Grafana Monitoring:" -ForegroundColor Green
Write-Host "  URL: http://localhost:3001" -ForegroundColor White
$grafanaPassword = [Environment]::GetEnvironmentVariable("GRAFANA_PASSWORD", "Process")
if ([string]::IsNullOrEmpty($grafanaPassword)) { $grafanaPassword = "admin123" }
Write-Host "  Login: admin / $grafanaPassword" -ForegroundColor White
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "1. Login to GoRules Studio" -ForegroundColor White
Write-Host "2. Create your first rule" -ForegroundColor White
Write-Host "3. Test via BRE Platform API" -ForegroundColor White
Write-Host "4. View metrics in Grafana" -ForegroundColor White
Write-Host ""
Write-Host "📖 Documentation: .\DEPLOYMENT_GUIDE.md" -ForegroundColor Yellow
Write-Host "📖 Rule Editing Guide: ..\docs\RULE_EDITING_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Cyan
Write-Host "To stop: docker-compose down" -ForegroundColor Cyan
Write-Host "To restart: docker-compose restart" -ForegroundColor Cyan
Write-Host ""

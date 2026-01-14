# Quick Start Guide for Windows

## Prerequisites

1. **Docker Desktop for Windows**
   - Download: https://docs.docker.com/desktop/install/windows-install/
   - Make sure Docker Desktop is running

2. **Git** (optional, for cloning repository)
   - Download: https://git-scm.com/download/win

## Quick Start (Automated)

### Step 1: Open PowerShell

Right-click on the Start menu and select **"Windows PowerShell"** or **"Windows Terminal"**

### Step 2: Navigate to deployment directory

```powershell
cd C:\Users\rsvij\.gemini\antigravity\scratch\gorules-bre-platform\deployment
```

### Step 3: Run the quick-start script

```powershell
.\quick-start.ps1
```

**Note**: If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Manual Start (Alternative)

If you prefer to run commands manually:

### Step 1: Create .env file

```powershell
cd C:\Users\rsvij\.gemini\antigravity\scratch\gorules-bre-platform\deployment
Copy-Item .env.example .env
notepad .env
```

Edit the `.env` file and set at minimum:
- `GITHUB_TOKEN=your_token_here`

### Step 2: Start services

```powershell
docker-compose up -d
```

### Step 3: Wait for services to start (2-3 minutes)

Check status:
```powershell
docker-compose ps
```

### Step 4: Access services

Open your browser:
- **GoRules Studio**: http://localhost:3000
- **BRE Platform API**: http://localhost:8000/docs
- **Keycloak**: http://localhost:8080
- **Grafana**: http://localhost:3001

## Troubleshooting

### Docker Desktop not running

**Error**: `error during connect: This error may indicate that the docker daemon is not running`

**Solution**: 
1. Open Docker Desktop
2. Wait for it to fully start
3. Try again

### Port already in use

**Error**: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**Solution**:
```powershell
# Find what's using the port
netstat -ano | findstr :3000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
```

### Execution Policy Error

**Error**: `cannot be loaded because running scripts is disabled on this system`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Services not starting

**Check logs**:
```powershell
docker-compose logs -f
```

**Restart specific service**:
```powershell
docker-compose restart gorules-studio
```

## Useful Commands

### View logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gorules-studio
```

### Stop services
```powershell
docker-compose down
```

### Restart services
```powershell
docker-compose restart
```

### Remove everything (clean slate)
```powershell
docker-compose down -v
```

### Check service health
```powershell
# GoRules Studio
Invoke-WebRequest http://localhost:3000/health

# BRE Platform
Invoke-WebRequest http://localhost:8000/health

# Keycloak
Invoke-WebRequest http://localhost:8080/health
```

## Next Steps

1. ✅ Services are running
2. 📖 Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. 📖 Read [Rule Editing Guide](../docs/RULE_EDITING_GUIDE.md)
4. 🎯 Login to GoRules Studio and create your first rule!

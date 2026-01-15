# GoRules BRE Platform - Simple Setup Guide

## Overview

This is a simplified setup of the GoRules Business Rule Engine platform designed for **development and testing**. It includes only the essential components:

- **Backend**: FastAPI-based Decision Gateway
- **Rule Engine**: GoRules Zen Engine for rule evaluation  
- **Rule Editor**: GoRules Studio for visual rule editing
- **Database**: PostgreSQL for audit logs and persistence

**Removed**: Authentication (Keycloak), Monitoring (Prometheus/Grafana), Reverse Proxy (Nginx), Git-sync

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **8GB RAM** minimum
- **Ports available**: 3000, 5432, 8000

## Quick Start

### Windows

```powershell
# Clone or navigate to the project directory
cd gorules-bre-platform

# Run the simple setup script
.\start-simple.ps1
```

### Linux/Mac

```bash
# Clone or navigate to the project directory
cd gorules-bre-platform

# Make the script executable
chmod +x start-simple.sh

# Run the simple setup script
./start-simple.sh
```

### Manual Start

```bash
# Start services
docker-compose -f docker-compose.simple.yml up -d

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop services
docker-compose -f docker-compose.simple.yml down
```

## Accessing Services

After startup (1-2 minutes), access:

| Service | URL | Description |
|---------|-----|-------------|
| **GoRules Studio** | http://localhost:3000 | Visual rule editor |
| **BRE Platform API** | http://localhost:8000/docs | Interactive API docs |
| **PostgreSQL** | localhost:5432 | Database (user: postgres, password: postgres) |

## Creating Your First Rule

### 1. Open GoRules Studio

Navigate to http://localhost:3000

### 2. Create a New Decision Table

1. Click **"New Decision"**
2. Choose **"Decision Table"**
3. Name it: `credit_approval`

### 3. Define Input/Output

**Inputs** (Facts):
- `credit_score` (number)
- `annual_income` (number)
- `employment_years` (number)

**Outputs**:
- `approved` (boolean)
- `reason` (string)

### 4. Add Rules

| Credit Score | Annual Income | Employment Years | Approved | Reason |
|--------------|---------------|------------------|----------|---------|
| >= 700 | >= 50000 | >= 2 | true | "Excellent credit profile" |
| >= 650 | >= 40000 | >= 1 | true | "Good credit profile" |
| < 650 | - | - | false | "Credit score too low" |
| - | < 40000 | - | false | "Income too low" |

### 5. Save the Rule

Save to: `rules/credit/credit_approval.json`

### 6. Test via API

Open http://localhost:8000/docs and try the `/api/v1/decisions/evaluate` endpoint:

```json
{
  "rule_name": "credit_approval",
  "facts": {
    "credit_score": 720,
    "annual_income": 60000,
    "employment_years": 3
  }
}
```

**Expected Response**:
```json
{
  "decision": {
    "approved": true,
    "reason": "Excellent credit profile"
  },
  "correlation_id": "...",
  "timestamp": "..."
}
```

## Project Structure

```
gorules-bre-platform/
├── app/                          # Backend application
│   ├── api/v1/endpoints/         # API endpoints
│   ├── services/                 # Rule engine service
│   ├── domain/                   # Fact models
│   └── main.py                   # FastAPI app
├── rules/                        # Rule definitions (JSON)
│   ├── credit/
│   │   └── credit_approval.json
│   └── kyc/
├── fact_registry/                # Fact definitions (YAML)
│   └── facts/
│       ├── credit_facts.yaml
│       └── kyc_facts.yaml
├── docker-compose.simple.yml     # Simplified Docker setup
├── start-simple.ps1              # Windows startup script
├── start-simple.sh               # Linux/Mac startup script
└── .env.simple                   # Environment configuration
```

## Development Workflow

### 1. Edit Rules

- Open GoRules Studio: http://localhost:3000
- Create/edit rules visually
- Rules are saved to `./rules/` directory
- Changes are immediately available to the backend

### 2. Test Rules

- Use the API docs: http://localhost:8000/docs
- Call `/api/v1/decisions/evaluate` with test data
- Check audit logs in PostgreSQL

### 3. View Logs

```bash
# All services
docker-compose -f docker-compose.simple.yml logs -f

# Specific service
docker-compose -f docker-compose.simple.yml logs -f bre-platform
```

### 4. Database Access

```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.simple.yml exec postgres psql -U postgres -d bre_platform

# View audit logs
SELECT * FROM decision_audit_logs ORDER BY created_at DESC LIMIT 10;
```

## Common Commands

```bash
# Start services
docker-compose -f docker-compose.simple.yml up -d

# Stop services
docker-compose -f docker-compose.simple.yml down

# Restart a service
docker-compose -f docker-compose.simple.yml restart bre-platform

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Clean reset (removes all data)
docker-compose -f docker-compose.simple.yml down -v

# Rebuild backend after code changes
docker-compose -f docker-compose.simple.yml up -d --build bre-platform
```

## Troubleshooting

### Port Already in Use

If ports 3000, 5432, or 8000 are already in use:

1. Edit `docker-compose.simple.yml`
2. Change the port mappings (e.g., `"3001:3000"`)
3. Restart services

### Services Not Starting

```bash
# Check service status
docker-compose -f docker-compose.simple.yml ps

# View detailed logs
docker-compose -f docker-compose.simple.yml logs

# Restart all services
docker-compose -f docker-compose.simple.yml restart
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.simple.yml exec postgres pg_isready -U postgres

# Restart PostgreSQL
docker-compose -f docker-compose.simple.yml restart postgres
```

### Rules Not Loading

1. Check rules are in `./rules/` directory
2. Verify JSON format is valid
3. Check backend logs: `docker-compose -f docker-compose.simple.yml logs bre-platform`
4. Restart backend: `docker-compose -f docker-compose.simple.yml restart bre-platform`

## API Endpoints

### Health Check
```
GET /health
```

### Evaluate Decision
```
POST /api/v1/decisions/evaluate
{
  "rule_name": "credit_approval",
  "facts": { ... }
}
```

### List Available Rules
```
GET /api/v1/rules
```

### Get Fact Registry
```
GET /api/v1/fact-registry/facts
```

## Next Steps

1. **Explore the API**: http://localhost:8000/docs
2. **Create more rules**: Use GoRules Studio
3. **Add fact definitions**: Edit files in `fact_registry/facts/`
4. **Write tests**: Add test cases in `tests/`
5. **Customize**: Modify `app/` code as needed

## Production Deployment

This simplified setup is **NOT suitable for production**. For production:

- Add authentication (Keycloak or similar)
- Add monitoring (Prometheus/Grafana)
- Add reverse proxy (Nginx)
- Use managed PostgreSQL
- Implement proper secrets management
- Add rate limiting and security headers
- Use the full `docker-compose.yml` instead

See `deployment/DEPLOYMENT_GUIDE.md` for production setup.

## Support

- **Documentation**: `docs/` directory
- **Architecture**: `docs/ARCHITECTURE.md`
- **Fact Registry**: `docs/FACT_REGISTRY.md`
- **Rule Modeling**: `docs/RULE_MODELING.md`

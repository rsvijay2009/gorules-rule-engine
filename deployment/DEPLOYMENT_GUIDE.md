# Self-Hosted GoRules Studio - Deployment Guide

## Overview

This guide walks you through deploying a complete, production-ready, self-hosted GoRules Studio on your infrastructure with:

- ✅ **GoRules Studio** (Visual rule editor)
- ✅ **Keycloak SSO** (Enterprise authentication)
- ✅ **PostgreSQL** (Audit logs, user data)
- ✅ **Nginx** (Reverse proxy, SSL termination)
- ✅ **Prometheus + Grafana** (Monitoring)
- ✅ **Git Integration** (Automatic rule sync)
- ✅ **Fact Registry Integration** (Governed facts)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet / Users                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Nginx (SSL)  │
                    │  Port 80/443  │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┬──────────────┐
        │                   │                   │              │
        ▼                   ▼                   ▼              ▼
┌──────────────┐    ┌──────────────┐    ┌──────────┐  ┌──────────┐
│   GoRules    │    │     BRE      │    │ Keycloak │  │ Grafana  │
│   Studio     │◄───┤   Platform   │◄───┤   SSO    │  │Monitoring│
│   :3000      │    │    :8000     │    │  :8080   │  │  :3000   │
└──────┬───────┘    └──────┬───────┘    └────┬─────┘  └────┬─────┘
       │                   │                  │             │
       │                   │                  │             │
       └───────────────────┼──────────────────┼─────────────┘
                           │                  │
                           ▼                  ▼
                   ┌──────────────┐    ┌──────────────┐
                   │  PostgreSQL  │    │  Prometheus  │
                   │    :5432     │    │    :9090     │
                   └──────────────┘    └──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │   Git Sync   │
                   │  (Sidecar)   │
                   └──────────────┘
```

## Prerequisites

### System Requirements

**Minimum (Development)**:
- 4 CPU cores
- 8 GB RAM
- 50 GB disk space
- Docker 20.10+
- Docker Compose 2.0+

**Recommended (Production)**:
- 8 CPU cores
- 16 GB RAM
- 200 GB SSD
- Docker 24.0+
- Docker Compose 2.20+

### Required Accounts/Access

1. **GitHub/GitLab** account with:
   - Repository for rules (e.g., `company/bre-rules`)
   - Personal Access Token (PAT) with `repo` scope

2. **Domain names** (or use localhost for testing):
   - `rules.company.com` → GoRules Studio
   - `bre-api.company.com` → BRE Platform API
   - `auth.company.com` → Keycloak SSO
   - `monitoring.company.com` → Grafana

3. **SSL Certificates** (for production):
   - Wildcard cert for `*.company.com`
   - Or individual certs for each subdomain

## Quick Start (Development)

### Step 1: Clone Repository

```bash
cd /opt  # Or your preferred location
git clone https://github.com/company/gorules-bre-platform.git
cd gorules-bre-platform
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp deployment/.env.example deployment/.env

# Edit with your values
nano deployment/.env
```

**Minimum required values**:
```bash
GITHUB_TOKEN=ghp_your_token_here
KEYCLOAK_ADMIN_PASSWORD=secure_password_123
```

### Step 3: Start Services

```bash
cd deployment
docker-compose up -d
```

**Wait 2-3 minutes** for all services to start.

### Step 4: Verify Services

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                STATUS
# gorules-studio      Up (healthy)
# bre-platform        Up (healthy)
# keycloak            Up
# postgres            Up (healthy)
# nginx               Up
# prometheus          Up
# grafana             Up
# git-sync            Up
```

### Step 5: Access Services

Open your browser:

1. **GoRules Studio**: http://localhost:3000
   - Login: `admin` / `admin123` (change on first login)

2. **BRE Platform API**: http://localhost:8000/docs
   - Interactive API documentation

3. **Keycloak Admin**: http://localhost:8080
   - Login: `admin` / `admin123`

4. **Grafana**: http://localhost:3001
   - Login: `admin` / `admin123`

## Production Deployment

### Step 1: Prepare Infrastructure

#### Option A: Single Server

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Option B: Kubernetes (Advanced)

See `deployment/k8s/README.md` for Kubernetes deployment.

### Step 2: Configure DNS

Point your domains to the server IP:

```
rules.company.com       A    203.0.113.10
bre-api.company.com     A    203.0.113.10
auth.company.com        A    203.0.113.10
monitoring.company.com  A    203.0.113.10
```

### Step 3: SSL Certificates

#### Option A: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d rules.company.com
sudo certbot certonly --standalone -d bre-api.company.com
sudo certbot certonly --standalone -d auth.company.com
sudo certbot certonly --standalone -d monitoring.company.com

# Copy to nginx directory
sudo cp /etc/letsencrypt/live/rules.company.com/fullchain.pem deployment/nginx/ssl/
sudo cp /etc/letsencrypt/live/rules.company.com/privkey.pem deployment/nginx/ssl/
```

#### Option B: Corporate Certificates

```bash
# Copy your certificates
cp /path/to/company-cert.crt deployment/nginx/ssl/
cp /path/to/company-key.key deployment/nginx/ssl/
```

### Step 4: Configure Production Settings

Edit `deployment/.env`:

```bash
# Production domains
GORULES_DOMAIN=rules.company.com
BRE_PLATFORM_DOMAIN=bre-api.company.com
KEYCLOAK_DOMAIN=auth.company.com
GRAFANA_DOMAIN=monitoring.company.com

# Strong passwords
KEYCLOAK_ADMIN_PASSWORD=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
GRAFANA_PASSWORD=$(openssl rand -base64 32)

# Git integration
GITHUB_TOKEN=ghp_your_production_token

# SMTP for notifications
SMTP_HOST=smtp.company.com
SMTP_PORT=587
SMTP_USER=notifications@company.com
SMTP_PASSWORD=your_smtp_password
```

### Step 5: Enable HTTPS in Nginx

Edit `deployment/nginx/nginx.conf`:

1. Uncomment all `listen 443 ssl http2;` lines
2. Uncomment SSL certificate paths
3. Uncomment HTTP → HTTPS redirect

### Step 6: Deploy

```bash
cd deployment

# Pull latest images
docker-compose pull

# Start in production mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 7: Configure Keycloak

1. Access Keycloak admin: https://auth.company.com
2. Login with admin credentials
3. Navigate to "Clients" → "gorules-studio"
4. Update redirect URIs to production domain:
   ```
   https://rules.company.com/*
   ```
5. Save changes

### Step 8: Configure Corporate SSO (Optional)

If using Active Directory / LDAP / SAML:

1. In Keycloak, go to "Identity Providers"
2. Add your corporate IdP (SAML, OIDC, LDAP)
3. Configure attribute mappings
4. Test login flow

## Configuration

### GoRules Studio Configuration

The studio is configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  # Git Integration
  - GIT_ENABLED=true
  - GIT_REPO_URL=https://github.com/company/bre-rules.git
  
  # Fact Registry (connects to BRE Platform)
  - FACT_REGISTRY_ENABLED=true
  - FACT_REGISTRY_URL=http://bre-platform:8000/api/v1/fact-registry/facts
  - FACT_REGISTRY_STRICT_MODE=true  # Only allow approved facts
  
  # Authentication
  - AUTH_ENABLED=true
  - AUTH_PROVIDER=oidc
  - OIDC_ISSUER_URL=http://keycloak:8080/realms/bre-platform
```

### RBAC Roles

Configured in Keycloak realm:

| Role | Permissions |
|------|-------------|
| `bre-admin` | Full access: create, edit, delete, approve rules |
| `bre-editor` | Create and edit rules (requires approval) |
| `bre-viewer` | Read-only access to rules |
| `bre-approver` | Approve rule changes |

### User Management

#### Add New User

1. Keycloak Admin → Users → Add User
2. Set username, email, first/last name
3. Credentials tab → Set password
4. Role Mappings → Assign roles (e.g., `bre-editor`)

#### Assign to Team

1. Groups → Select group (e.g., "Risk Team")
2. Members → Add user

## Git Integration

### Repository Structure

Your Git repository should have this structure:

```
bre-rules/
├── rules/
│   ├── kyc/
│   │   └── pan_eligibility_v1.json
│   ├── aml/
│   │   └── risk_scoring_v1.json
│   └── credit/
│       └── loan_approval_v1.json
├── fact_registry/
│   └── facts/
│       ├── kyc_facts.yaml
│       ├── aml_facts.yaml
│       └── credit_facts.yaml
└── tests/
    └── kyc/
        └── pan_eligibility_test.yaml
```

### Automatic Sync

The `git-sync` sidecar automatically pulls changes every 60 seconds:

```yaml
git-sync:
  environment:
    - GIT_SYNC_WAIT=60  # Sync every 60 seconds
```

**To force immediate sync**:
```bash
docker-compose restart git-sync
```

### Webhook Integration (Instant Updates)

For instant rule updates on Git push:

1. In GitHub/GitLab, go to Settings → Webhooks
2. Add webhook:
   - URL: `https://bre-api.company.com/webhooks/git`
   - Content type: `application/json`
   - Events: `push`
3. Save

Now rules update within seconds of Git push!

## Monitoring

### Grafana Dashboards

Access Grafana: https://monitoring.company.com

**Pre-configured dashboards**:

1. **BRE Platform Overview**
   - Request rate, latency, error rate
   - Rule evaluation performance
   - Decision breakdown (approved/rejected)

2. **GoRules Studio Usage**
   - Active users
   - Rule edits per day
   - Most edited rules

3. **System Health**
   - CPU, memory, disk usage
   - Database connections
   - Network traffic

### Prometheus Metrics

Key metrics exposed:

```
# BRE Platform
bre_decision_requests_total{status="approved"}
bre_decision_latency_seconds{quantile="0.95"}
bre_rule_evaluation_duration_seconds

# GoRules Studio
gorules_active_users
gorules_rule_edits_total
gorules_git_sync_errors_total
```

### Alerts (Optional)

Configure alerts in `prometheus/alerts.yml`:

```yaml
groups:
  - name: bre_platform
    rules:
      - alert: HighErrorRate
        expr: rate(bre_decision_errors_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate in BRE platform"
```

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
docker exec postgres pg_dump -U postgres bre_platform > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i postgres psql -U postgres bre_platform < backup_20260114.sql
```

### Rule Backup

Rules are in Git - just ensure Git repository is backed up.

### Full System Backup

```bash
# Backup volumes
docker run --rm \
  -v deployment_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore
docker run --rm \
  -v deployment_postgres-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

## Scaling

### Horizontal Scaling (Multiple Instances)

Edit `docker-compose.yml`:

```yaml
bre-platform:
  deploy:
    replicas: 3  # Run 3 instances
```

Nginx will automatically load balance.

### Vertical Scaling (More Resources)

```yaml
bre-platform:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
```

## Troubleshooting

### GoRules Studio Won't Start

```bash
# Check logs
docker-compose logs gorules-studio

# Common issues:
# 1. Git token invalid → Update GITHUB_TOKEN in .env
# 2. Keycloak not ready → Wait 2 minutes, restart studio
# 3. Port conflict → Change port in docker-compose.yml
```

### Can't Login to Studio

```bash
# Check Keycloak is running
docker-compose ps keycloak

# Reset admin password
docker exec -it keycloak /opt/keycloak/bin/kc.sh \
  --realm bre-platform \
  --user admin \
  --password new_password_123
```

### Rules Not Syncing

```bash
# Check git-sync logs
docker-compose logs git-sync

# Verify Git token
docker exec git-sync git ls-remote https://github.com/company/bre-rules.git

# Force sync
docker-compose restart git-sync
```

### High Latency

```bash
# Check Prometheus metrics
curl http://localhost:9090/api/v1/query?query=bre_decision_latency_seconds

# Check database connections
docker exec postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Increase resources if needed
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall (only ports 80, 443 open)
- [ ] Enable Keycloak brute force protection
- [ ] Set up regular database backups
- [ ] Configure audit log retention
- [ ] Enable Nginx rate limiting
- [ ] Use strong Git tokens (rotate every 90 days)
- [ ] Configure SMTP for security alerts
- [ ] Set up intrusion detection (fail2ban)

## Maintenance

### Updates

```bash
# Pull latest images
docker-compose pull

# Restart with new images (zero downtime)
docker-compose up -d --no-deps --build bre-platform
```

### Log Rotation

```bash
# Configure in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Health Checks

```bash
# All services
curl http://localhost:3000/health  # GoRules Studio
curl http://localhost:8000/health  # BRE Platform
curl http://localhost:8080/health  # Keycloak
```

## Support

- **Documentation**: https://docs.gorules.io
- **Community**: https://github.com/gorules/zen
- **Enterprise Support**: support@gorules.io
- **Internal**: #bre-platform-support (Slack)

## Next Steps

1. ✅ Deploy self-hosted studio
2. ✅ Configure SSO
3. ✅ Create first rule
4. ✅ Test decision API
5. ✅ Set up monitoring
6. 📖 Read [Rule Editing Guide](../docs/RULE_EDITING_GUIDE.md)
7. 📖 Read [Best Practices](../docs/BEST_PRACTICES.md)

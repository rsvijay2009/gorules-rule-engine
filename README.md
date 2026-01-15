# Enterprise Business Rule Engine Platform (GoRules + FastAPI)

## 🚀 Quick Start (Single Command)

**To start all services** (Backend, Database, and Visual Rule Editor) at once:

```powershell
# Windows
.\start-simple.ps1
```

```bash
# Linux / macOS
chmod +x start-simple.sh && ./start-simple.sh
```

📖 **See [QUICK_START.md](QUICK_START.md) for a unified platform guide.**

---

## Overview

Production-grade Business Rule Engine platform for regulated fintech companies. Enables business users to manage rules visually without backend deployments while maintaining auditability, governance, and performance.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Business Users                            │
│                   (Risk, Compliance, Ops)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GoRules Visual Rule Editor                      │
│              (Decision Tables / Decision Graphs)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Rule Repository (Git)                          │
│              (Versioned, Auditable, Rollbackable)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GoRules Runtime (Zen Engine)                   │
│                    (Stateless Evaluation)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Decision Gateway (This Repo)                │
│         • Correlation IDs  • Audit Logs  • Observability         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│          Fact Adapter (Anti-Corruption Layer)                    │
│         Backend DTOs → Canonical Fact Models                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Core Domain Services                            │
│              (KYC, AML, Credit, Fraud, etc.)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **No Hardcoded Rules**: All business logic lives in GoRules
2. **Zero-Deployment Rule Changes**: Update rules without backend restarts
3. **Fact Governance**: Centralized Fact Registry with PR-based approval
4. **Auditability**: Every decision logged with fact snapshots & rule versions
5. **Stateless**: Horizontal scaling, no session state
6. **Type Safety**: Strong typing from Fact Registry → Canonical Models → Rules

## Project Structure

```
gorules-bre-platform/
├── app/
│   ├── api/v1/endpoints/       # Decision endpoints
│   ├── core/                   # Config, security, logging
│   ├── services/               # Engine wrapper, audit service
│   ├── domain/                 # Canonical fact models (versioned)
│   ├── adapters/               # Fact adapters (ACL)
│   └── schemas/                # Request/response contracts
├── fact_registry/              # Central fact governance
│   ├── schema.json             # Fact registry JSON schema
│   └── facts/                  # Domain fact definitions
│       ├── kyc_facts.yaml
│       ├── aml_facts.yaml
│       └── credit_facts.yaml
├── rules/                      # GoRules decision definitions
│   ├── kyc/
│   │   └── pan_eligibility.json
│   └── aml/
│       └── risk_scoring.json
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FACT_REGISTRY.md
│   ├── RULE_MODELING.md
│   └── ANTI_PATTERNS.md
└── deployment/
    ├── docker-compose.yml
    └── k8s/
```

## Quick Start

### Simple Setup (Recommended for Development)

```bash
# Windows
.\start-simple.ps1

# Linux/Mac
chmod +x start-simple.sh && ./start-simple.sh
```

See [SIMPLE_SETUP.md](SIMPLE_SETUP.md) for detailed instructions.

### Full Setup (Production)

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run with Docker (full stack)
docker-compose up

# Run tests
pytest tests/ -v
```

See [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) for production deployment.

## Core Components

### 1. Fact Registry
Central source of truth for all business facts. See [FACT_REGISTRY.md](docs/FACT_REGISTRY.md)

### 2. Canonical Fact Models
Versioned domain models consumed by rules. See [domain/](app/domain/)

### 3. Fact Adapters
Anti-Corruption Layer mapping backend DTOs to canonical facts. See [adapters/](app/adapters/)

### 4. Decision Gateway
FastAPI endpoints exposing decision capabilities. See [api/](app/api/)

## Security & Compliance

- **RBAC**: Role-based access control for rule editing
- **Audit Logs**: Decision logs + change logs
- **Environment Isolation**: Dev/Test/Prod separation
- **Correlation IDs**: End-to-end request tracing

## Performance Targets

- **Latency**: < 10ms p95 for rule evaluation
- **Throughput**: 10,000+ TPS per instance
- **Availability**: 99.99% uptime

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Fact Registry Guide](docs/FACT_REGISTRY.md)
- [Rule Modeling Guide](docs/RULE_MODELING.md)
- [Anti-Patterns](docs/ANTI_PATTERNS.md)

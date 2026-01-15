# GoRules BRE Platform - Quick Reference

## 🚀 Start Platform

```powershell
# Windows
.\start-simple.ps1

# Linux/Mac
./start-simple.sh
```

## 🌐 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| GoRules Studio | http://localhost:3000 | Visual rule editor |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| PostgreSQL | localhost:5432 | Database (postgres/postgres) |

## 📝 Test API

### Credit Approval Example

```bash
curl -X POST "http://localhost:8000/api/v1/decisions/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "credit_approval_v1",
    "facts": {
      "credit_score": 720,
      "annual_income": 60000,
      "employment_years": 3
    }
  }'
```

### KYC Eligibility Example

```bash
curl -X POST "http://localhost:8000/api/v1/decisions/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "pan_eligibility_v1",
    "facts": {
      "pan_verification_status": "VERIFIED",
      "pan_name_match_score": 0.92,
      "customer_age": 28,
      "cibil_score": 720,
      "cibil_fetch_status": "SUCCESS",
      "dedupe_match_found": false
    }
  }'
```

## 🛠️ Common Commands

```bash
# View logs
docker-compose -f docker-compose.simple.yml logs -f

# View specific service logs
docker-compose -f docker-compose.simple.yml logs -f bre-platform

# Stop services
docker-compose -f docker-compose.simple.yml down

# Restart a service
docker-compose -f docker-compose.simple.yml restart bre-platform

# Clean reset (removes all data)
docker-compose -f docker-compose.simple.yml down -v

# Rebuild after code changes
docker-compose -f docker-compose.simple.yml up -d --build bre-platform
```

## 📂 Project Structure

```
gorules-bre-platform/
├── rules/                    # Add your rules here (JSON)
│   ├── credit/
│   └── kyc/
├── fact_registry/facts/      # Add fact definitions here (YAML)
├── app/                      # Backend code
└── tests/                    # Tests
```

## 🎯 Workflow

1. **Edit Rules** → Open http://localhost:3000
2. **Save Rules** → Rules saved to `./rules/` directory
3. **Test Rules** → Use API at http://localhost:8000/docs
4. **View Logs** → Check audit logs in PostgreSQL

## 🔍 Database Access

```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.simple.yml exec postgres psql -U postgres -d bre_platform

# View audit logs
SELECT * FROM decision_audit_logs ORDER BY created_at DESC LIMIT 10;
```

## 📚 Documentation

- **Setup Guide**: [SIMPLE_SETUP.md](SIMPLE_SETUP.md)
- **Walkthrough**: [walkthrough.md](C:\Users\rsvij\.gemini\antigravity\brain\a33c4ab9-1fd0-4111-9d90-719dd1fd4a2e\walkthrough.md)
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Fact Registry**: [docs/FACT_REGISTRY.md](docs/FACT_REGISTRY.md)

## ⚠️ Troubleshooting

### Port Already in Use
Edit `docker-compose.simple.yml` and change port mappings

### Services Not Starting
```bash
docker-compose -f docker-compose.simple.yml ps
docker-compose -f docker-compose.simple.yml logs
```

### Rules Not Loading
1. Check rules are in `./rules/` directory
2. Verify JSON format is valid
3. Restart backend: `docker-compose -f docker-compose.simple.yml restart bre-platform`

## 🎓 Example Rules

### Credit Approval
- **File**: `rules/credit/credit_approval_v1.json`
- **Inputs**: credit_score, annual_income, employment_years
- **Outputs**: approved, reason, credit_limit

### KYC Eligibility
- **File**: `rules/kyc/pan_eligibility_v1.json`
- **Inputs**: PAN details, age, CIBIL score, dedupe status
- **Outputs**: kyc_eligibility_status, kyc_rejection_reason

## 🔐 Security Note

This simplified setup has **NO AUTHENTICATION** and is for **DEVELOPMENT ONLY**.

For production, use the full deployment with Keycloak, monitoring, and security features.

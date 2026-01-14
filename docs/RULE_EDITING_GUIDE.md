# Rule Editing Guide for Business Users

## Overview

Business users (Risk, Compliance, Operations teams) can edit rules **visually** using the **GoRules Editor** without writing code or requiring backend deployments. This guide explains the complete workflow.

## Architecture: How Rule Editing Works

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Business User Opens GoRules Editor (Web UI)            │
│  https://editor.gorules.io or Self-Hosted GoRules Studio        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Load Existing Rule from Git Repository                 │
│  - User selects rule (e.g., "KYC PAN Eligibility v1")           │
│  - Editor loads JSON definition from rules/ directory            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Edit Rule Visually (No Code!)                          │
│  - Drag & drop decision tables                                  │
│  - Select facts from dropdown (governed by Fact Registry)       │
│  - Define conditions using visual operators                     │
│  - Set output values                                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Test Rule in Editor                                    │
│  - Provide sample input facts                                   │
│  - See decision output immediately                              │
│  - Validate logic before saving                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Save & Create Pull Request (PR)                        │
│  - Save rule as JSON to Git branch                              │
│  - Create PR with change description                            │
│  - Tag reviewers (Risk Manager, Compliance)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Automated Validation (CI/CD)                           │
│  - Schema validation (valid JSON)                               │
│  - Fact Registry validation (all facts exist & active)          │
│  - Backward compatibility check                                 │
│  - Automated tests run                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 7: Human Review & Approval                                │
│  - Risk Manager reviews business logic                          │
│  - Compliance reviews regulatory impact                         │
│  - Tech Lead reviews technical correctness                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 8: Merge to Main & Auto-Deploy                            │
│  - PR merged to main branch                                     │
│  - Rule automatically deployed to production                    │
│  - NO backend restart required!                                 │
│  - Change audit log created                                     │
└─────────────────────────────────────────────────────────────────┘
```

## GoRules Editor Options

### Option 1: GoRules Cloud Editor (Recommended for Quick Start)
- **URL**: https://editor.gorules.io
- **Pros**: No installation, always up-to-date, collaborative
- **Cons**: Requires internet, data leaves your network
- **Best for**: Development, testing, small teams

### Option 2: Self-Hosted GoRules Studio (Enterprise)
- **Deployment**: Docker container on your infrastructure
- **Pros**: Full control, data stays internal, customizable
- **Cons**: Requires infrastructure setup
- **Best for**: Production, regulated environments, large teams

### Option 3: VS Code Extension (For Technical Users)
- **Extension**: GoRules for VS Code
- **Pros**: Integrated with development workflow
- **Cons**: Requires VS Code knowledge
- **Best for**: Technical business analysts, developers

## Step-by-Step: Editing a Rule

### 1. Open GoRules Editor

**Cloud Editor:**
```
1. Navigate to https://editor.gorules.io
2. Click "Open from Git" or "Import File"
3. Select your rule JSON file (e.g., rules/kyc/pan_eligibility_v1.json)
```

**Self-Hosted:**
```
1. Navigate to your company's GoRules Studio URL
2. Login with SSO credentials
3. Select rule from repository browser
```

### 2. Understand the Visual Interface

The GoRules Editor shows:

```
┌─────────────────────────────────────────────────────────────────┐
│  Canvas (Drag & Drop)                                            │
│                                                                   │
│   ┌──────────┐      ┌──────────────┐      ┌──────────┐          │
│   │  Input   │─────▶│  Decision    │─────▶│  Output  │          │
│   │  Facts   │      │  Table       │      │  Result  │          │
│   └──────────┘      └──────────────┘      └──────────┘          │
│                                                                   │
│  Decision Table Editor (Double-click to edit):                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ IF customer_age | IF cibil_score | THEN kyc_status        │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │ >= 21           | >= 650         | APPROVED               │  │
│  │ >= 21           | < 650          | REJECTED               │  │
│  │ < 21            | -              | REJECTED               │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Edit Decision Logic

**Example: Change CIBIL threshold from 650 to 700**

1. **Double-click** the "KYC Eligibility Decision" table
2. Find the row: `IF cibil_score >= 650 THEN APPROVED`
3. Click on `650` and change to `700`
4. Click "Save"

**That's it!** No code, no deployment.

### 4. Add a New Rule Row

**Example: Add special handling for premium customers**

1. Click "Add Row" in the decision table
2. Set conditions:
   - `customer_type = "PREMIUM"`
   - `cibil_score >= 600` (lower threshold for premium)
3. Set output:
   - `kyc_eligibility_status = "APPROVED"`
4. **Important**: Drag row to correct priority (first-match wins)

### 5. Use Fact Dropdown (Governed)

When adding conditions, you **cannot type free text**. You must:

1. Click "Add Input Column"
2. Select from dropdown of **approved facts only**:
   ```
   ✓ customer_age (integer)
   ✓ cibil_score (integer)
   ✓ pan_verification_status (enum: VERIFIED, INVALID, ...)
   ✓ customer_state (enum: KARNATAKA, MAHARASHTRA, ...)
   ✗ random_field_name (NOT IN REGISTRY - CANNOT USE)
   ```

This prevents typos and ensures all facts are governed.

### 6. Test Your Changes

Before saving, **always test**:

1. Click "Test" tab in editor
2. Provide sample input:
   ```json
   {
     "customer_age": 25,
     "cibil_score": 720,
     "pan_verification_status": "VERIFIED",
     "dedupe_match_found": false
   }
   ```
3. Click "Run"
4. Verify output:
   ```json
   {
     "kyc_eligibility_status": "APPROVED",
     "kyc_rejection_reason": null
   }
   ```

### 7. Save & Create Pull Request

**In GoRules Editor:**
1. Click "Save to Git"
2. Enter commit message:
   ```
   Update CIBIL threshold from 650 to 700
   
   Reason: Risk team decision to reduce default risk
   Ticket: RISK-1234
   ```
3. Create new branch: `rule/kyc-cibil-threshold-update`
4. Push to repository

**In GitHub/GitLab:**
1. Navigate to your repository
2. You'll see: "Create Pull Request" button
3. Click it, add reviewers:
   - Risk Manager (business approval)
   - Compliance Officer (regulatory approval)
   - Tech Lead (technical approval)
4. Submit PR

### 8. Wait for Approval & Deployment

**Automated Checks Run:**
- ✅ JSON schema validation
- ✅ All facts exist in Fact Registry
- ✅ All facts are ACTIVE (not DEPRECATED)
- ✅ Rule can be parsed by engine
- ✅ Automated tests pass

**Human Reviews:**
- Risk Manager: "Approved - aligns with new risk policy"
- Compliance: "Approved - no regulatory impact"
- Tech Lead: "Approved - technically sound"

**Merge & Deploy:**
1. PR merged to `main`
2. **Automatic deployment** (no manual steps!)
3. Rule goes live in **< 5 minutes**
4. **No backend restart needed**

## Governance & Safety

### Fact Registry Governance

**Problem**: Without governance, users might create facts like:
- `customerAge` (camelCase)
- `customer_age` (snake_case)
- `age` (ambiguous)
- `cust_age` (abbreviation)

**Solution**: Fact Registry enforces:
1. **Central approval**: All facts must be in `fact_registry/facts/*.yaml`
2. **PR-based changes**: New facts require approval
3. **Dropdown selection**: Editor only shows approved facts
4. **Lifecycle management**: Facts can be DEPRECATED gracefully

### Rule Versioning

Every rule change creates a new version:

```
rules/kyc/pan_eligibility_v1.json
  ├─ v1.0.0 (initial)
  ├─ v1.1.0 (added premium customer logic)
  ├─ v1.2.0 (changed CIBIL threshold)
  └─ v1.2.1 (bug fix)
```

**Rollback**: If a rule causes issues, simply revert the Git commit.

### Environment Isolation

Rules are deployed to environments separately:

```
Development:   rules/dev/kyc/pan_eligibility_v1.json
Testing:       rules/test/kyc/pan_eligibility_v1.json
Production:    rules/prod/kyc/pan_eligibility_v1.json
```

**Promotion workflow**:
1. Edit in `dev`
2. Test in `test`
3. Promote to `prod` (requires approval)

## Common Workflows

### Workflow 1: Emergency Rule Change

**Scenario**: Fraud spike detected, need to tighten rules immediately.

1. **Create hotfix branch**: `hotfix/fraud-emergency-2026-01-14`
2. **Edit rule** in GoRules Editor (increase fraud threshold)
3. **Test thoroughly** with recent fraud cases
4. **Create PR** with "URGENT" label
5. **Fast-track approval** (Risk + Compliance only, skip others)
6. **Merge & deploy** (live in 5 minutes)
7. **Monitor** decision logs for impact

### Workflow 2: Scheduled Rule Update

**Scenario**: Quarterly policy update (e.g., new state restrictions).

1. **Create feature branch**: `feature/q1-2026-policy-update`
2. **Edit multiple rules** as needed
3. **Schedule PR review** for policy committee meeting
4. **Get approvals** from all stakeholders
5. **Schedule merge** for policy effective date
6. **Deploy automatically** at scheduled time

### Workflow 3: A/B Testing Rules

**Scenario**: Test new CIBIL threshold (650 vs 700).

1. **Create two rule versions**:
   - `pan_eligibility_v1_control.json` (650 threshold)
   - `pan_eligibility_v1_experiment.json` (700 threshold)
2. **Deploy both** to production
3. **Backend randomly selects** which rule to use (50/50 split)
4. **Monitor metrics** (approval rate, default rate)
5. **Promote winner** after statistical significance

## Best Practices

### ✅ DO

1. **Always test** before creating PR
2. **Write clear commit messages** with ticket IDs
3. **Use descriptive rule names** (e.g., `pan_eligibility_v1`, not `rule1`)
4. **Add comments** in decision tables (use `_description` field)
5. **Keep rules simple** (avoid complex nested logic)
6. **Version incrementally** (v1.0.0 → v1.1.0, not v1 → v5)

### ❌ DON'T

1. **Don't hardcode values** in rules (use configuration facts instead)
2. **Don't create free-text facts** (always use Fact Registry)
3. **Don't skip testing** (untested rules cause production issues)
4. **Don't merge without approval** (governance exists for a reason)
5. **Don't put business logic in code** (rules belong in GoRules)
6. **Don't create duplicate facts** (check registry first)

## Training & Support

### For New Business Users

**Week 1**: GoRules Editor basics
- How to open/edit/save rules
- Understanding decision tables
- Testing rules

**Week 2**: Fact Registry & governance
- How to request new facts
- Understanding fact lifecycle
- Fact naming conventions

**Week 3**: Advanced rule modeling
- Decision graphs (multiple tables)
- Complex conditions
- Performance optimization

### Getting Help

- **Slack**: #bre-platform-support
- **Documentation**: https://docs.gorules.io
- **Office Hours**: Tuesdays 2-3 PM with Platform Team
- **Escalation**: platform-team@company.com

## Technical Details (For Reference)

### How Rules Are Loaded (Zero Downtime)

```python
# Backend polls Git repository every 60 seconds
# OR uses webhook for instant updates

def load_rules():
    # 1. Fetch latest from Git
    git pull origin main
    
    # 2. Parse rule JSON
    rule_def = json.load("rules/kyc/pan_eligibility_v1.json")
    
    # 3. Update in-memory cache
    rule_cache["kyc/pan_eligibility_v1"] = rule_def
    
    # 4. Next request uses new rule
    # NO RESTART REQUIRED!
```

### Rule Execution Flow

```
API Request
  ↓
Fact Adapter (map DTO → canonical facts)
  ↓
Load Rule from Cache (or Git)
  ↓
GoRules Engine Evaluates
  ↓
Decision Output
  ↓
Audit Log
  ↓
API Response
```

**Performance**: < 10ms per decision (including rule evaluation)

## Summary

Business users edit rules **visually** using GoRules Editor, with:

✅ **No code** required
✅ **No deployments** required
✅ **Governed facts** (dropdown selection)
✅ **PR-based approval** workflow
✅ **Automated validation** (CI/CD)
✅ **Instant deployment** (< 5 minutes)
✅ **Full audit trail** (who, what, when, why)
✅ **Rollback capability** (Git revert)

This enables **business agility** while maintaining **enterprise governance**.

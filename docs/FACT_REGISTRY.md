# Fact Registry Guide

## Overview

The **Fact Registry** is the central source of truth for all business facts used in rules. It enforces governance, prevents typos, and ensures consistency across the platform.

## Why Fact Registry?

### Without Fact Registry ❌

```
Business User A creates: customer_age
Business User B creates: customerAge
Business User C creates: age
Developer creates: cust_age
```

**Result**: 4 different names for the same concept!

### With Fact Registry ✅

```
Approved fact: customer_age (integer, 18-120)
```

**Result**: Everyone uses the same name, type, and constraints.

## Fact Registry Schema

Every fact must have:

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | ✅ | snake_case name (e.g., `customer_age`) |
| `type` | ✅ | Data type: `string`, `integer`, `number`, `boolean`, `date`, `datetime`, `enum` |
| `description` | ✅ | Clear business description |
| `owner` | ✅ | Team responsible (e.g., `kyc-team`) |
| `lifecycle_state` | ✅ | `DRAFT`, `ACTIVE`, `DEPRECATED`, `RETIRED` |
| `version` | ✅ | Fact version (e.g., `v1`) |
| `source_system` | ✅ | Originating system (e.g., `kyc-service`) |
| `allowed_values` | ⚠️ | For `enum` types only |
| `default_value` | ⬜ | Optional default if missing |
| `validation_rules` | ⬜ | Optional constraints (min, max, pattern) |

## Example Fact Definition

```yaml
- name: customer_age
  type: integer
  description: "Customer's age in years calculated from date of birth"
  owner: kyc-team
  lifecycle_state: ACTIVE
  version: v1
  source_system: customer-db
  validation_rules:
    min: 18
    max: 120
  tags:
    - kyc
    - demographic
  examples:
    - 25
    - 42
    - 65
```

## Fact Lifecycle

```
DRAFT → ACTIVE → DEPRECATED → RETIRED
```

### DRAFT
- Fact is being designed
- Not available in GoRules Editor
- Can be freely modified

### ACTIVE
- Fact is approved and available
- Visible in GoRules Editor dropdown
- Can be used in rules
- Changes require PR approval

### DEPRECATED
- Fact is being phased out
- Still works but shows warning
- New rules should use replacement fact
- Set `deprecated_by` field

### RETIRED
- Fact is no longer available
- Removed from GoRules Editor
- Existing rules using it will fail validation

## Governance Workflow

### Adding a New Fact

1. **Create PR** with new fact in `fact_registry/facts/*.yaml`

```yaml
# fact_registry/facts/kyc_facts.yaml
- name: pan_verification_status
  type: enum
  description: "Status of PAN verification from Karza"
  owner: kyc-team
  lifecycle_state: DRAFT  # Start as DRAFT
  version: v1
  source_system: karza-api
  allowed_values:
    - "VERIFIED"
    - "NOT_VERIFIED"
    - "INVALID"
    - "PENDING"
    - "ERROR"
```

2. **CI/CD validates**:
   - Schema compliance
   - No duplicate names
   - Valid enum values
   - Naming conventions

3. **Reviewers approve**:
   - Domain owner (e.g., KYC team lead)
   - Platform team (technical review)
   - Compliance (if PII/sensitive)

4. **Merge & activate**:
   - Change `lifecycle_state` to `ACTIVE`
   - Fact appears in GoRules Editor

### Deprecating a Fact

1. **Create replacement fact** (if needed)

```yaml
- name: customer_age_v2
  type: integer
  lifecycle_state: ACTIVE
  # ... other fields
```

2. **Mark old fact as DEPRECATED**

```yaml
- name: customer_age
  lifecycle_state: DEPRECATED
  deprecated_by: customer_age_v2
  deprecated_date: "2026-01-14"
  retirement_date: "2026-04-14"  # 90 days notice
```

3. **Update all rules** to use new fact

4. **Retire old fact** after grace period

## Fact Naming Conventions

### ✅ Good Names

- `customer_age` (clear, snake_case)
- `pan_verification_status` (descriptive)
- `cibil_score` (standard acronym)
- `dedupe_match_found` (boolean, clear intent)

### ❌ Bad Names

- `customerAge` (camelCase, not snake_case)
- `age` (ambiguous - customer? account? loan?)
- `status` (too generic)
- `flag1` (meaningless)
- `temp_field` (temporary fields don't belong in registry)

## Integration with GoRules Editor

### Fact Registry API

```python
# app/api/v1/endpoints/fact_registry.py

@router.get("/facts")
async def get_all_facts():
    """Return all ACTIVE facts for GoRules Editor"""
    facts = load_facts_from_yaml("fact_registry/facts/kyc_facts.yaml")
    
    return {
        "facts": [
            {
                "name": f["name"],
                "type": f["type"],
                "description": f["description"],
                "allowed_values": f.get("allowed_values"),
            }
            for f in facts["facts"]
            if f["lifecycle_state"] == "ACTIVE"
        ]
    }
```

### GoRules Editor Configuration

```javascript
{
  "factRegistry": {
    "enabled": true,
    "apiUrl": "https://bre-api.company.com/api/v1/fact-registry/facts",
    "strictMode": true  // Only allow facts from registry
  }
}
```

When `strictMode` is enabled:
- Users can only select facts from dropdown
- Free-text fact entry is disabled
- Typos are impossible

## Fact Versioning

### When to Version

Create a new version when:
- Changing data type (e.g., `string` → `enum`)
- Changing allowed values (breaking change)
- Changing semantic meaning

### How to Version

```yaml
# v1 (original)
- name: customer_state
  type: string
  version: v1

# v2 (changed to enum)
- name: customer_state
  type: enum
  version: v2
  allowed_values:
    - "KARNATAKA"
    - "MAHARASHTRA"
    # ...
```

Rules specify which version they use:
```json
{
  "fact_model_version": "v2",
  "inputs": ["customer_state"]
}
```

## Ownership & Responsibilities

### Domain Teams (KYC, AML, Credit)
- Define facts for their domain
- Maintain fact accuracy
- Review fact change requests
- Update facts when business requirements change

### Platform Team
- Maintain Fact Registry infrastructure
- Enforce schema compliance
- Provide tooling (validation scripts, CI/CD)
- Review technical correctness

### Compliance Team
- Review PII/sensitive facts
- Ensure regulatory compliance
- Approve fact deprecation/retirement

## Best Practices

### ✅ DO

1. **Use descriptive names**: `pan_verification_status` not `status`
2. **Add examples**: Help users understand valid values
3. **Tag appropriately**: `pii`, `sensitive`, `regulatory`
4. **Set validation rules**: Prevent invalid data
5. **Document source system**: Know where fact comes from
6. **Version breaking changes**: Don't break existing rules

### ❌ DON'T

1. **Don't use abbreviations**: `cust_age` → `customer_age`
2. **Don't create duplicates**: Check registry first
3. **Don't skip review**: All facts need approval
4. **Don't retire without notice**: Give 90-day warning
5. **Don't use free-text**: Always use registry
6. **Don't bypass governance**: No "temporary" facts

## Monitoring

### Fact Usage Metrics

Track which facts are used most:

```sql
SELECT 
    fact_name,
    COUNT(*) as usage_count
FROM decision_audit_logs
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY fact_name
ORDER BY usage_count DESC;
```

### Unused Facts

Identify facts that are never used:

```sql
SELECT name 
FROM fact_registry 
WHERE lifecycle_state = 'ACTIVE'
  AND name NOT IN (
    SELECT DISTINCT fact_name 
    FROM decision_audit_logs
  );
```

Consider deprecating unused facts.

## Summary

The Fact Registry provides:

✅ **Governance**: PR-based approval for all facts
✅ **Consistency**: Single source of truth
✅ **Type Safety**: Strong typing enforced
✅ **Discoverability**: All facts documented
✅ **Lifecycle Management**: DRAFT → ACTIVE → DEPRECATED → RETIRED
✅ **Integration**: Direct integration with GoRules Editor

**Remember**: Every fact must be in the registry. No exceptions.

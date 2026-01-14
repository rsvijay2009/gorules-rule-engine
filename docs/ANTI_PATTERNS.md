# Anti-Patterns to Avoid in BRE Platform

## Overview

This document lists **critical anti-patterns** that must be avoided when building or maintaining the Business Rule Engine platform. These are common mistakes that violate the core architectural principles.

---

## ❌ ANTI-PATTERN 1: Hardcoding Business Rules in Backend Code

### What NOT to do:

```python
# ❌ BAD: Business logic in FastAPI endpoint
@app.post("/kyc/check")
def check_kyc(customer: Customer):
    if customer.age < 21:
        return {"status": "REJECTED", "reason": "AGE_TOO_LOW"}
    
    if customer.cibil_score < 650:
        return {"status": "REJECTED", "reason": "LOW_CREDIT"}
    
    return {"status": "APPROVED"}
```

### Why it's wrong:
- Requires deployment to change thresholds (age, CIBIL score)
- Business users cannot edit rules
- No audit trail of rule changes
- Tight coupling between business logic and code

### What to do instead:

```python
# ✅ GOOD: Delegate to GoRules
@app.post("/kyc/check")
def check_kyc(customer: Customer):
    facts = adapter.adapt(customer)
    decision = rule_engine.evaluate("kyc/eligibility_v1.json", facts)
    return decision
```

---

## ❌ ANTI-PATTERN 2: Free-Text Fact Names in Rules

### What NOT to do:

```json
{
  "rules": [
    {
      "if": "customerAge >= 21",  // ❌ Typo: should be customer_age
      "then": "approved"
    }
  ]
}
```

### Why it's wrong:
- Typos cause runtime failures
- No governance or standardization
- Duplicate facts with different names (`customer_age`, `customerAge`, `age`)
- No type safety

### What to do instead:

1. **Fact Registry** with approved facts only
2. **Dropdown selection** in GoRules Editor (no free text)
3. **CI/CD validation** to catch unapproved facts

---

## ❌ ANTI-PATTERN 3: Exposing Backend DTOs to Rules

### What NOT to do:

```python
# ❌ BAD: Pass raw backend DTO to rules
customer_dto = get_customer_from_db(customer_id)
decision = rule_engine.evaluate(rule, customer_dto.dict())
```

### Why it's wrong:
- Rules depend on backend implementation details
- Changing DB schema breaks rules
- No normalization (enums, nulls, defaults)
- Violates separation of concerns

### What to do instead:

```python
# ✅ GOOD: Use Fact Adapter (Anti-Corruption Layer)
customer_dto = get_customer_from_db(customer_id)
canonical_facts = fact_adapter.adapt(customer_dto)
decision = rule_engine.evaluate(rule, canonical_facts)
```

---

## ❌ ANTI-PATTERN 4: Rule Logic in API Controllers

### What NOT to do:

```python
# ❌ BAD: Business logic in controller
@app.post("/loan/approve")
def approve_loan(request: LoanRequest):
    # Complex business logic here
    if request.amount > 100000:
        if request.cibil_score < 750:
            return reject()
    
    if request.employment_type == "self_employed":
        if request.income < 50000:
            return reject()
    
    return approve()
```

### Why it's wrong:
- Cannot change logic without deployment
- No visual representation for business users
- Hard to test and maintain

### What to do instead:

```python
# ✅ GOOD: Thin controller, delegate to rules
@app.post("/loan/approve")
def approve_loan(request: LoanRequest):
    facts = adapter.adapt(request)
    decision = rule_engine.evaluate("loan/approval_v1.json", facts)
    await audit_service.log_decision(decision)
    return decision
```

---

## ❌ ANTI-PATTERN 5: Data Transformations Inside Rules

### What NOT to do:

```json
{
  "rules": [
    {
      "if": "customer_age * 12 > 252",  // ❌ Calculation in rule
      "then": "approved"
    }
  ]
}
```

### Why it's wrong:
- Rules should contain only comparisons, not transformations
- Hard to understand business intent
- Performance overhead

### What to do instead:

```python
# ✅ GOOD: Transform in Fact Adapter, compare in rule
class FactAdapter:
    def adapt(self, customer):
        return {
            "customer_age_months": customer.age * 12,  # Transform here
        }

# Rule just compares
{
  "if": "customer_age_months > 252",
  "then": "approved"
}
```

---

## ❌ ANTI-PATTERN 6: Missing Audit Logs

### What NOT to do:

```python
# ❌ BAD: No audit logging
decision = rule_engine.evaluate(rule, facts)
return decision  # No record of what happened
```

### Why it's wrong:
- Cannot explain decisions to customers
- No regulatory compliance
- Cannot debug production issues
- No analytics on decision patterns

### What to do instead:

```python
# ✅ GOOD: Comprehensive audit logging
decision = rule_engine.evaluate(rule, facts)

await audit_service.log_decision(
    correlation_id=correlation_id,
    rule_path=rule_path,
    input_facts=facts,  # Complete snapshot
    decision_output=decision,
    rule_version=rule_version,
)

return decision
```

---

## ❌ ANTI-PATTERN 7: Stateful Rule Evaluation

### What NOT to do:

```python
# ❌ BAD: Storing state in rule engine
class RuleEngine:
    def __init__(self):
        self.previous_decisions = {}  # ❌ State!
    
    def evaluate(self, facts):
        # Use previous decisions in evaluation
        if self.previous_decisions.get(facts["customer_id"]):
            return cached_result
```

### Why it's wrong:
- Cannot horizontally scale
- Race conditions in concurrent requests
- Hard to test and debug

### What to do instead:

```python
# ✅ GOOD: Stateless evaluation
class RuleEngine:
    def evaluate(self, rule, facts):
        # Pure function: same input → same output
        return engine.evaluate(rule, facts)
```

---

## ❌ ANTI-PATTERN 8: No Rule Versioning

### What NOT to do:

```bash
# ❌ BAD: Overwrite rule file
rules/kyc_eligibility.json  # No version info
```

### Why it's wrong:
- Cannot rollback to previous version
- No audit trail of changes
- Cannot A/B test rules

### What to do instead:

```bash
# ✅ GOOD: Versioned rules
rules/kyc/pan_eligibility_v1.json
rules/kyc/pan_eligibility_v2.json

# Or Git tags
git tag rule-kyc-v1.2.3
```

---

## ❌ ANTI-PATTERN 9: Skipping Rule Validation

### What NOT to do:

```python
# ❌ BAD: Deploy rule without validation
git add rules/new_rule.json
git commit -m "new rule"
git push  # No validation!
```

### Why it's wrong:
- Invalid rules cause production failures
- Typos in fact names
- Missing required fields

### What to do instead:

```yaml
# ✅ GOOD: CI/CD validation pipeline
- name: Validate Rules
  run: |
    python scripts/validate_rule_schema.py
    python scripts/validate_facts.py
    pytest tests/rules/
```

---

## ❌ ANTI-PATTERN 10: Backend Depends on Rule Names

### What NOT to do:

```python
# ❌ BAD: Hardcoded rule names in code
if customer.type == "premium":
    decision = evaluate("premium_kyc_rule.json", facts)
else:
    decision = evaluate("standard_kyc_rule.json", facts)
```

### Why it's wrong:
- Renaming rules breaks backend
- Tight coupling
- Cannot add new customer types without deployment

### What to do instead:

```python
# ✅ GOOD: Configuration-driven rule selection
rule_path = config.get_rule_for_domain("kyc", customer.type)
decision = evaluate(rule_path, facts)

# Or even better: single rule handles all cases
decision = evaluate("kyc/eligibility_v1.json", facts)
```

---

## ❌ ANTI-PATTERN 11: No Default Values for Missing Facts

### What NOT to do:

```python
# ❌ BAD: Assume all facts are present
facts = {
    "customer_age": customer.age,
    "cibil_score": customer.cibil_score,  # What if None?
}
```

### Why it's wrong:
- Runtime errors when facts are missing
- Rules fail unexpectedly

### What to do instead:

```python
# ✅ GOOD: Handle missing facts gracefully
facts = {
    "customer_age": customer.age,
    "cibil_score": customer.cibil_score or 0,  # Default
    "cibil_fetch_status": "SUCCESS" if customer.cibil_score else "NO_HISTORY",
}
```

---

## ❌ ANTI-PATTERN 12: Mixing Environments

### What NOT to do:

```bash
# ❌ BAD: Same rules for dev/test/prod
rules/kyc_eligibility.json  # Used everywhere
```

### Why it's wrong:
- Cannot test rule changes safely
- Production incidents from untested rules

### What to do instead:

```bash
# ✅ GOOD: Environment isolation
rules/dev/kyc_eligibility.json
rules/test/kyc_eligibility.json
rules/prod/kyc_eligibility.json

# Or Git branches
git checkout dev    # Development rules
git checkout prod   # Production rules
```

---

## Summary Checklist

Before deploying, verify:

- [ ] No business logic in backend code
- [ ] All facts are in Fact Registry
- [ ] Fact Adapter used (no raw DTOs to rules)
- [ ] Controllers are thin (delegate to rules)
- [ ] No transformations inside rules
- [ ] Comprehensive audit logging
- [ ] Stateless rule evaluation
- [ ] Rules are versioned
- [ ] CI/CD validation pipeline
- [ ] Backend doesn't depend on rule names
- [ ] Default values for missing facts
- [ ] Environment isolation (dev/test/prod)

---

**Remember**: The goal is **business agility** with **enterprise governance**. Anti-patterns sacrifice one or both of these goals.

# KYC Eligibility Rules: Analysis & User Guide

This document explains the behavior of the KYC eligibility engine, provides test scenarios, and guides business users on how to manage rules.

## 1. Analysis of the Reported Scenario

### Input Summary
- **PAN Verification Status**: `VERIFIED`
- **CIBIL Score**: `550`
- **Correlation ID**: `550e8400-e29b-41d4-a716-446655440000`

### Why was it rejected with `PAN_INVALID`?
Even though you provided `"pan_verification_status": "VERIFIED"`, the system rejected it due to an internal data mapping mismatch in the **Anti-Corruption Layer (Fact Adapter)**.

#### The Execution Trace:
1. **API Layer**: The API receives your request and prepares a "Karza DTO". It converts `VERIFIED` to lowercase `verified`.
2. **Fact Adapter**: The adapter maps vendor-specific statuses to canonical rule-engine statuses.
   - It expects: `"valid"`, `"invalid"`, `"pending"`, or `"error"`.
   - Your input: `"verified"` (lowercase) is provided.
   - **Result**: Because `"verified"` is not in the expected list, the system falls back to a default status of **`ERROR`**.
3. **Rule Engine**: The rules evaluate the status `ERROR`.
   - Inside [pan_eligibility_v1.json](file:///c:/Users/rsvij/.gemini/antigravity/scratch/gorules-bre-platform/rules/kyc/pan_eligibility_v1.json), the "PAN Validation" table has a rule:
     - If status is `ERROR` → `pan_check_passed = false` and `rejection_reason = "PAN_INVALID"`.
4. **Final Decision**: The "KYC Eligibility Decision" table sees `pan_check_passed = false` and immediately rejects the application with the reason provided (`PAN_INVALID`).

> [!NOTE]
> Even if the PAN check had passed, this application would have been rejected for **`CIBIL_SCORE_LOW`** because the score (550) is below the rule threshold of **650**.

---

## 2. Testing Multiple Scenarios

To help you validate the rules, here are several scenarios you can test using `curl`.

### Scenario 1: Approved Customer
**Criteria**: PAN Verified, Score >= 650, Age >= 21, No Dedupe.
*Note: Use `valid` instead of `VERIFIED` to bypass the current mapping limitation.*

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/decisions/kyc/eligibility' \
  -H 'Content-Type: application/json' \
  -d '{
  "pan_verification_status": "valid",
  "pan_name_match_score": 0.95,
  "cibil_score": 750,
  "cibil_fetch_status": "SUCCESS",
  "customer_age": 30,
  "customer_state": "KARNATAKA",
  "customer_type": "RETAIL",
  "dedupe_match_found": false,
  "pan_number": "ABCDE1234F"
}'
```

### Scenario 2: Rejected - Low CIBIL Score
**Criteria**: Score < 650.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/decisions/kyc/eligibility' \
  -H 'Content-Type: application/json' \
  -d '{
  "pan_verification_status": "valid",
  "pan_name_match_score": 0.95,
  "cibil_score": 500,
  "cibil_fetch_status": "SUCCESS",
  "customer_age": 30,
  "customer_state": "KARNATAKA",
  "customer_type": "RETAIL",
  "dedupe_match_found": false,
  "pan_number": "ABCDE1234F"
}'
```

### Scenario 3: Manual Review - No CIBIL History
**Criteria**: CIBIL status is `NO_HISTORY`.

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/decisions/kyc/eligibility' \
  -H 'Content-Type: application/json' \
  -d '{
  "pan_verification_status": "valid",
  "pan_name_match_score": 0.95,
  "cibil_fetch_status": "NO_HISTORY",
  "customer_age": 30,
  "customer_state": "KARNATAKA",
  "customer_type": "RETAIL",
  "dedupe_match_found": false,
  "pan_number": "ABCDE1234F"
}'
```

---

## 3. Business User Guide: Editing Rules

The rules are stored in a GoRules JSON format. You can edit [pan_eligibility_v1.json](file:///c:/Users/rsvij/.gemini/antigravity/scratch/gorules-bre-platform/rules/kyc/pan_eligibility_v1.json) directly or via the GoRules Studio.

### How to change a threshold (e.g., CIBIL Score)

1. Find the `decision-table-eligibility` node in the JSON.
2. Look for the `rules` array.
3. Locate the rule with `_description": "CIBIL score too low"`.
4. Change the value for `input-3`.

**Example: Increase minimum CIBIL score to 700**
```json
// Find this rule:
{
  "_description": "CIBIL score too low",
  "input-1": "true",
  "input-2": ">= 21",
  "input-3": "< 650",  // <-- CHANGE THIS TO "< 700"
  "input-4": "\"SUCCESS\"",
  "output-1": "\"REJECTED\"",
  "output-2": "\"CIBIL_SCORE_LOW\""
}
```

### How to change the Rejection Reason
If you want to change the error code returned to the customer:
1. Locate the `output-2` field in the relevant rule.
2. Update the string value.

### Key Concepts for Editors
- **Hit Policy**: Set to `"first"`, meaning the engine stops at the first rule that matches. Order matters!
- **Expressions**: 
  - `> 18`: Greater than 18.
  - `[21..60]`: Age between 21 and 60 (inclusive).
  - `"VERIFIED"`: Exact string match (must include internal double quotes in the JSON).
  - `null`: Matches when a value is empty or missing.

### Best Practices
- **Always version your rules**: Save a copy before making major changes.
- **Test after editing**: Use the `curl` commands above to ensure your changes work as expected.
- **Description**: Always add a `_description` to your rules so other team members know the intent.

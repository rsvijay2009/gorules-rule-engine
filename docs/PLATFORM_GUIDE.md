# BRE Platform: Unified Implementation & Usage Guide

## 🌟 Overview
This platform is a production-ready **Business Rule Engine (BRE)** built on the **GoRules Zen Engine**. It enables business teams (Risk, Compliance, Operations) to manage complex logic visually while providing developers with a high-performance, stateless API for decision-making.

---

## 🏗️ Architecture for Technical Teams

The platform follows a decoupled architecture ensuring maximum agility and reliability.

### 1. Decision Gateway (FastAPI Backend)
The core engine that evaluates rules. It is stateless and optimized for high-throughput.
- **Rule Engine**: Embedded **Zen Engine** (Rust core) for ultra-fast evaluations (<10ms).
- **Service Layer**: `MockRuleEngineService` manages rule loading, caching, and evaluation.
- **Management APIs**: Endpoints to list, read, and save rules directly to the filesystem (Git-ready).

### 2. JDM Studio (Next.js Frontend)
A professional, full-screen modeling environment.
- **Visual Modeling**: Drag-and-drop nodes for Decision Tables, Scripts, and Functions.
- **Live Simulation**: In-context testing with execution path highlighting on the graph.
- **Edge-to-Edge Workspace**: Optimized for complex decision models.

### 3. Shared Rule Infrastructure
- **Filesystem Storage**: Rules are stored as JSON files, making them easily versionable via Git.
- **Fact Registry**: A central source of truth for all business facts used in decisions.

---

## 💼 Business Value & Governance

### No-Code Agility
Business users can update logic (e.g., CIBIL thresholds, age limits) via a visual interface. No developer intervention or code deployments are needed for business changes.

### Bulletproof Governance
The **Fact Registry** ensures that everyone uses the same terminology.
- **Consistency**: Prevents `customer_age` vs `custAge` confusion.
- **Type Safety**: Enforces data types (e.g., age must be an integer).
- **Compliance**: PR-based approval workflow for all rule and fact changes.

---

## 🚀 How to Use the Platform

### 1. Adding & Customizing Rules
1. **Open Studio**: Navigate to `http://localhost:3000`.
2. **Select Rule**: Click on an existing rule (e.g., `kyc/pan_eligibility_v1`).
3. **Visual Edit**: 
    - **Decision Table**: Double-click to edit rows and columns.
    - **Add Logic**: Use the "Add Row" button to include new scenarios.
    - **Fact Selection**: Use the integrated dropdowns to select governed facts.
4. **Test & Save**: Run a simulation in the right-side panel and click **Save Rule**.

### 2. Integration in FastAPI
To use a rule in your backend, simply call the evaluation service:

```python
from app.services.rule_engine import MockRuleEngineService

# Initialize the engine
rule_engine = MockRuleEngineService(rules_directory="./rules")

# Input Facts (Context)
facts = {
    "customer_age": 28,
    "cibil_score": 720,
    "pan_verification_status": "VERIFIED"
}

# Evaluate the rule
result = rule_engine.evaluate(
    rule_path="kyc/pan_eligibility_v1.json",
    facts=facts
)

print(result)
# Output: {"kyc_eligibility_status": "APPROVED", "performance": "2ms", ...}
```

### 3. Using the Fact Registry
The Fact Registry acts as a contract between business and technology.

**Example Fact Definition (`fact_registry/facts/kyc_facts.yaml`):**
```yaml
- name: cibil_score
  type: integer
  description: "CIBIL TransUnion score of the applicant"
  owner: credit-risk
  lifecycle_state: ACTIVE
  validation_rules:
    min: 300
    max: 900
```
- **Usage**: Once defined here, the JDM Studio will automatically show `cibil_score` in the editor's fact selection dropdown.

---

## 📊 Practical Examples

### Example 1: KYC Eligibility (Business View)
- **Rule**: "If the customer is over 21 AND their PAN is VERIFIED, then APPROVE."
- **Studio Model**: 
    - **Input Node**: Maps incoming JSON facts.
    - **Decision Table**: 
        - `customer_age >= 21`
        - `pan_verification_status == "VERIFIED"`
    - **Output Node**: Returns `{"status": "APPROVED"}`.

### Example 2: Dynamic Pricing (Technical View)
- **Goal**: Apply a discount based on customer loyalty.
- **Backend call**:
```python
# FastAPI Endpoint
@app.post("/pricing")
async def get_price(customer_data: dict):
    # BRE evaluates the business-defined pricing tiers
    decision = rule_engine.evaluate("pricing/loyalty_v1.json", customer_data)
    return {"final_price": base_price * decision["discount_multiplier"]}
```

---

## 🛠️ Setup & Development
1. **Start Engine & Studio**:
   ```powershell
   .\start-simple.ps1
   ```
2. **Access Studio**: `http://localhost:3000`
3. **Internal Management Hub**: `http://localhost:8000/docs` (Rule Management APIs)

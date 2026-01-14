# GoRules Integration Architecture

## Overview

This document explains how the FastAPI Decision Gateway integrates with GoRules for visual rule editing and stateless execution.

## GoRules Components

### 1. GoRules Editor (Visual Rule Authoring)

**What it is**: Web-based visual editor for creating decision tables and decision graphs.

**Deployment Options**:

#### Option A: GoRules Cloud (SaaS)
```
URL: https://editor.gorules.io
Pros: No setup, always updated, collaborative
Cons: Data leaves your network
Use case: Development, testing, POC
```

#### Option B: Self-Hosted GoRules Studio (Enterprise)
```yaml
# docker-compose.yml
version: '3.8'
services:
  gorules-studio:
    image: gorules/studio:latest
    ports:
      - "3000:3000"
    environment:
      - GIT_INTEGRATION=true
      - GIT_REPO_URL=https://github.com/company/bre-rules.git
      - AUTH_PROVIDER=okta  # SSO integration
      - FACT_REGISTRY_URL=https://bre-platform/fact-registry
    volumes:
      - ./rules:/app/rules
```

**Key Features**:
- Drag-and-drop decision tables
- Fact selection from dropdown (integrated with Fact Registry)
- Real-time testing
- Git integration (save directly to repository)
- Collaboration (comments, version history)

### 2. GoRules Zen Engine (Runtime Evaluation)

**What it is**: Stateless rule execution engine (written in Rust, available as npm package or REST API).

**Integration Options**:

#### Option A: Python SDK (Recommended)
```python
# Install
pip install zen-engine

# Usage
from zen_engine import ZenEngine

engine = ZenEngine()
result = engine.evaluate(rule_definition, input_facts)
```

#### Option B: REST API (Microservice)
```yaml
# docker-compose.yml
services:
  zen-engine:
    image: gorules/zen-engine:latest
    ports:
      - "8080:8080"
    environment:
      - RULES_SOURCE=git  # Load rules from Git
      - GIT_REPO_URL=https://github.com/company/bre-rules.git
      - POLL_INTERVAL=60  # Refresh rules every 60 seconds
```

```python
# FastAPI calls Zen Engine API
import httpx

async def evaluate_rule(rule_path: str, facts: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://zen-engine:8080/evaluate",
            json={"rule": rule_path, "context": facts}
        )
        return response.json()
```

#### Option C: Embedded (For High Performance)
```python
# Embed Zen Engine directly in FastAPI process
# Lowest latency, no network hop
from zen_engine import ZenEngine

class RuleEngineService:
    def __init__(self):
        self.engine = ZenEngine()
        self.rules = self._load_rules_from_git()
    
    def evaluate(self, rule_path: str, facts: dict):
        rule_def = self.rules[rule_path]
        return self.engine.evaluate(rule_def, facts)
```

## Rule Storage & Versioning

### Git-Based Rule Repository

```
bre-rules/  (Git repository)
├── rules/
│   ├── kyc/
│   │   ├── pan_eligibility_v1.json
│   │   ├── pan_eligibility_v2.json
│   │   └── aadhaar_verification_v1.json
│   ├── aml/
│   │   └── risk_scoring_v1.json
│   └── credit/
│       └── loan_approval_v1.json
├── fact_registry/
│   ├── schema.json
│   └── facts/
│       ├── kyc_facts.yaml
│       ├── aml_facts.yaml
│       └── credit_facts.yaml
└── tests/
    └── kyc/
        └── pan_eligibility_v1_test.yaml
```

### Rule Loading Strategies

#### Strategy 1: Polling (Simple)
```python
import time
import threading
from git import Repo

class RuleLoader:
    def __init__(self, repo_path: str, poll_interval: int = 60):
        self.repo_path = repo_path
        self.poll_interval = poll_interval
        self.rules_cache = {}
        
        # Start background polling
        threading.Thread(target=self._poll_loop, daemon=True).start()
    
    def _poll_loop(self):
        while True:
            self._refresh_rules()
            time.sleep(self.poll_interval)
    
    def _refresh_rules(self):
        # Pull latest from Git
        repo = Repo(self.repo_path)
        repo.remotes.origin.pull()
        
        # Reload all rules
        self.rules_cache = self._load_all_rules()
        logger.info("Rules refreshed from Git")
```

#### Strategy 2: Webhook (Instant)
```python
from fastapi import APIRouter

webhook_router = APIRouter()

@webhook_router.post("/webhooks/git")
async def git_webhook(payload: dict):
    """
    GitHub/GitLab webhook endpoint
    Triggered on push to main branch
    """
    if payload.get("ref") == "refs/heads/main":
        # Pull latest rules
        rule_loader.refresh_rules()
        logger.info("Rules refreshed via webhook")
    
    return {"status": "ok"}
```

#### Strategy 3: Watch (Development)
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RuleFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.json'):
            # Reload specific rule
            rule_loader.reload_rule(event.src_path)
            logger.info(f"Rule reloaded: {event.src_path}")

observer = Observer()
observer.schedule(RuleFileHandler(), path="./rules", recursive=True)
observer.start()
```

## Fact Registry Integration

### Exposing Fact Registry to GoRules Editor

```python
# app/api/v1/endpoints/fact_registry.py

from fastapi import APIRouter
import yaml

router = APIRouter(prefix="/fact-registry", tags=["Fact Registry"])

@router.get("/facts")
async def get_all_facts():
    """
    Return all ACTIVE facts for GoRules Editor dropdown
    """
    facts = load_facts_from_yaml("fact_registry/facts/kyc_facts.yaml")
    
    # Filter only ACTIVE facts
    active_facts = [
        {
            "name": f["name"],
            "type": f["type"],
            "description": f["description"],
            "allowed_values": f.get("allowed_values"),
        }
        for f in facts["facts"]
        if f["lifecycle_state"] == "ACTIVE"
    ]
    
    return {"facts": active_facts}

@router.get("/facts/{domain}")
async def get_domain_facts(domain: str):
    """
    Return facts for specific domain (kyc, aml, credit)
    """
    facts = load_facts_from_yaml(f"fact_registry/facts/{domain}_facts.yaml")
    return {"facts": facts["facts"]}
```

### GoRules Editor Configuration

```javascript
// gorules-editor-config.js
{
  "factRegistry": {
    "enabled": true,
    "apiUrl": "https://bre-platform.company.com/api/v1/fact-registry/facts",
    "refreshInterval": 300,  // Refresh every 5 minutes
    "strictMode": true  // Only allow facts from registry
  },
  "git": {
    "enabled": true,
    "provider": "github",
    "repo": "company/bre-rules",
    "branch": "main"
  },
  "testing": {
    "enabled": true,
    "apiUrl": "https://bre-platform.company.com/api/v1/decisions/test"
  }
}
```

## Rule Validation Pipeline (CI/CD)

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-rules.yml
name: Validate Rules

on:
  pull_request:
    paths:
      - 'rules/**'
      - 'fact_registry/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate Rule JSON Schema
        run: |
          for rule in rules/**/*.json; do
            echo "Validating $rule"
            python scripts/validate_rule_schema.py "$rule"
          done
      
      - name: Validate Facts Against Registry
        run: |
          python scripts/validate_facts.py
      
      - name: Check Backward Compatibility
        run: |
          python scripts/check_compatibility.py
      
      - name: Run Rule Tests
        run: |
          pytest tests/ -v
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '✅ All rule validations passed!'
            })
```

### Validation Scripts

```python
# scripts/validate_facts.py
"""
Validate that all facts used in rules exist in Fact Registry
"""

import json
import yaml
from pathlib import Path

def load_fact_registry():
    facts = {}
    for fact_file in Path("fact_registry/facts").glob("*.yaml"):
        data = yaml.safe_load(fact_file.read_text())
        for fact in data["facts"]:
            facts[fact["name"]] = fact
    return facts

def extract_facts_from_rule(rule_path):
    rule = json.loads(Path(rule_path).read_text())
    facts_used = set()
    
    # Extract from decision tables
    for node in rule.get("nodes", []):
        if node["type"] == "decisionTableNode":
            for input_col in node["content"]["inputs"]:
                facts_used.add(input_col["field"])
    
    return facts_used

def validate():
    registry = load_fact_registry()
    errors = []
    
    for rule_path in Path("rules").rglob("*.json"):
        facts_used = extract_facts_from_rule(rule_path)
        
        for fact in facts_used:
            if fact not in registry:
                errors.append(f"{rule_path}: Unknown fact '{fact}'")
            elif registry[fact]["lifecycle_state"] != "ACTIVE":
                errors.append(
                    f"{rule_path}: Fact '{fact}' is {registry[fact]['lifecycle_state']}"
                )
    
    if errors:
        print("\n".join(errors))
        exit(1)
    else:
        print("✅ All facts validated successfully")

if __name__ == "__main__":
    validate()
```

## Deployment Architecture

### Production Deployment

```yaml
# deployment/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bre-platform
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: fastapi
        image: bre-platform:latest
        env:
        - name: RULES_SOURCE
          value: "git"
        - name: GIT_REPO_URL
          value: "https://github.com/company/bre-rules.git"
        - name: RULES_REFRESH_INTERVAL
          value: "60"  # Poll every 60 seconds
        volumeMounts:
        - name: rules-cache
          mountPath: /app/rules
      
      # Sidecar: Git sync container
      - name: git-sync
        image: k8s.gcr.io/git-sync:v3.6.0
        env:
        - name: GIT_SYNC_REPO
          value: "https://github.com/company/bre-rules.git"
        - name: GIT_SYNC_BRANCH
          value: "main"
        - name: GIT_SYNC_ROOT
          value: "/rules"
        - name: GIT_SYNC_WAIT
          value: "60"
        volumeMounts:
        - name: rules-cache
          mountPath: /rules
      
      volumes:
      - name: rules-cache
        emptyDir: {}
```

### High Availability Setup

```
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ BRE Instance │    │ BRE Instance │    │ BRE Instance │
│   (Pod 1)    │    │   (Pod 2)    │    │   (Pod 3)    │
│              │    │              │    │              │
│ + Git Sync   │    │ + Git Sync   │    │ + Git Sync   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Git Repository │
                  │   (Rules)       │
                  └─────────────────┘
```

**Key Points**:
- Each instance independently syncs rules from Git
- No shared state between instances
- Horizontal scaling (add more pods)
- Zero downtime deployments

## Performance Considerations

### Rule Caching

```python
from functools import lru_cache
import hashlib

class RuleEngineService:
    def __init__(self):
        self.engine = ZenEngine()
        self.rule_cache = {}
    
    @lru_cache(maxsize=1000)
    def get_rule_hash(self, rule_path: str) -> str:
        """Cache rule content hash to detect changes"""
        rule_content = Path(rule_path).read_text()
        return hashlib.sha256(rule_content.encode()).hexdigest()
    
    def load_rule(self, rule_path: str):
        current_hash = self.get_rule_hash(rule_path)
        
        if rule_path in self.rule_cache:
            cached_hash, cached_rule = self.rule_cache[rule_path]
            if cached_hash == current_hash:
                return cached_rule  # Use cached version
        
        # Load and cache new version
        rule_def = json.loads(Path(rule_path).read_text())
        self.rule_cache[rule_path] = (current_hash, rule_def)
        return rule_def
```

### Performance Targets

- **Rule Loading**: < 100ms (from cache)
- **Rule Evaluation**: < 10ms (p95)
- **End-to-End API**: < 50ms (p95)
- **Rule Refresh**: < 5 seconds (from Git push to live)

## Summary

The GoRules integration provides:

✅ **Visual editing** (no code for business users)
✅ **Git-based versioning** (full audit trail)
✅ **Stateless execution** (horizontal scaling)
✅ **Hot reload** (no restarts required)
✅ **Fact governance** (registry integration)
✅ **CI/CD validation** (automated checks)
✅ **High performance** (< 10ms evaluation)

This architecture enables **business agility** with **enterprise reliability**.

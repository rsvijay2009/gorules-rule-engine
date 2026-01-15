"""
Rule Management Endpoints

Allows visual editor to list, read, and save business rules.
"""

import os
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.services.rule_engine import MockRuleEngineService, RuleEvaluationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rules", tags=["Rule Management"])

RULES_DIR = Path(settings.RULES_DIR)
rule_engine = MockRuleEngineService(rules_directory=settings.RULES_DIR)  # Use the same engine as the main app

class RuleFile(BaseModel):
    name: str
    path: str
    is_directory: bool

class RuleUpdate(BaseModel):
    content: Dict[str, Any]

@router.get("/", response_model=List[RuleFile])
async def list_rules():
    """List all rule files in the rules directory"""
    if not RULES_DIR.exists():
        return []
    
    rules = []
    # Walk through the rules directory
    for root, dirs, files in os.walk(RULES_DIR):
        rel_root = os.path.relpath(root, RULES_DIR)
        if rel_root == ".":
            rel_root = ""
            
        for f in files:
            if f.endswith(".json"):
                rules.append(RuleFile(
                    name=f,
                    path=os.path.join(rel_root, f).replace("\\", "/"),
                    is_directory=False
                ))
    return rules

@router.get("/{path:path}")
async def get_rule(path: str):
    """Get the content of a specific rule file"""
    file_path = RULES_DIR / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Rule not found")
    
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading rule {path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{path:path}")
async def update_rule(path: str, update: RuleUpdate):
    """Update a specific rule file"""
    file_path = RULES_DIR / path
    
    # Security check: Ensure the path is within the rules directory
    try:
        file_path.resolve().relative_to(RULES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid path")

    # Create directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, "w") as f:
            json.dump(update.content, f, indent=2)
        
        # Clear engine cache to pick up changes
        rule_engine.reload_rules()
        
        return {"status": "success", "path": path}
    except Exception as e:
        logger.error(f"Error saving rule {path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class RuleTestRequest(BaseModel):
    path: str
    facts: Dict[str, Any]

@router.post("/test")
async def test_rule(request: RuleTestRequest):
    """Evaluate a rule with provided facts"""
    try:
        # Note: In a real scenario, we might want to test the rule 
        # WITHOUT saving it first. For now, we evaluate the saved file.
        result = rule_engine.evaluate(
            rule_path=request.path,
            facts=request.facts
        )
        return result
    except Exception as e:
        logger.error(f"Error testing rule {request.path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
GoRules Engine Service

Wrapper around GoRules Zen Engine for rule evaluation.

IMPORTANT:
- This service is stateless
- Rules are loaded from repository (file system or API)
- No business logic here - pure engine wrapper
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

try:
    from zen_engine import ZenEngine  # type: ignore
    ZEN_ENGINE_AVAILABLE = True
except ImportError:
    ZenEngine = None
    ZEN_ENGINE_AVAILABLE = False


logger = logging.getLogger(__name__)


class RuleEngineService:
    """
    GoRules Zen Engine wrapper service
    
    Responsibilities:
    1. Load rules from repository
    2. Execute rules with input facts
    3. Return decision output
    4. Handle engine errors gracefully
    """
    
    def __init__(self, rules_directory: str = "rules"):
        """
        Initialize the rule engine service
        
        Args:
            rules_directory: Path to directory containing rule JSON files
        """
        self.rules_directory = Path(rules_directory)
        if ZEN_ENGINE_AVAILABLE and ZenEngine:
            self.engine = ZenEngine()
        else:
            self.engine = None
            logger.warning("ZenEngine is not available. Real rule evaluation will fail.")
            
        self._rule_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"RuleEngineService initialized with rules_dir={rules_directory}")
    
    def load_rule(self, rule_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load a rule definition from file
        
        Args:
            rule_path: Relative path to rule file (e.g., "kyc/pan_eligibility_v1.json")
            use_cache: Whether to use cached rule (default: True)
            
        Returns:
            Rule definition as dictionary
        """
        if use_cache and rule_path in self._rule_cache:
            logger.debug(f"Using cached rule: {rule_path}")
            return self._rule_cache[rule_path]
        
        full_path = self.rules_directory / rule_path
        
        try:
            with open(full_path, 'r') as f:
                rule_def = json.load(f)
            
            self._rule_cache[rule_path] = rule_def
            logger.info(f"Loaded rule: {rule_path}")
            return rule_def
            
        except FileNotFoundError:
            logger.error(f"Rule file not found: {full_path}")
            raise ValueError(f"Rule not found: {rule_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid rule JSON: {full_path}, error: {e}")
            raise ValueError(f"Invalid rule format: {rule_path}")
    
    def evaluate(
        self,
        rule_path: str,
        facts: Dict[str, Any],
        trace: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluate a rule with given facts
        
        Args:
            rule_path: Path to rule file
            facts: Input facts as dictionary
            trace: Whether to include execution trace (default: False)
            
        Returns:
            Decision output dictionary
        """
        try:
            # Load rule definition
            rule_def = self.load_rule(rule_path)
            
            # Execute rule
            start_time = datetime.utcnow()
            result = self.engine.evaluate(rule_def, facts)
            end_time = datetime.utcnow()
            
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.info(
                f"Rule evaluated: {rule_path}",
                extra={
                    "rule_path": rule_path,
                    "execution_time_ms": execution_time_ms,
                    "correlation_id": facts.get("correlation_id"),
                }
            )
            
            # Add metadata to result
            result["_metadata"] = {
                "rule_path": rule_path,
                "execution_time_ms": execution_time_ms,
                "evaluation_timestamp": end_time.isoformat(),
            }
            
            if trace:
                result["_metadata"]["trace"] = result.get("trace", [])
            
            return result
            
        except Exception as e:
            logger.error(
                f"Rule evaluation failed: {e}",
                extra={
                    "rule_path": rule_path,
                    "correlation_id": facts.get("correlation_id"),
                }
            )
            raise RuleEvaluationError(f"Rule evaluation failed: {e}") from e
    
    def reload_rules(self) -> None:
        """
        Clear rule cache to force reload
        
        Use this when rules are updated without restarting the service.
        """
        self._rule_cache.clear()
        logger.info("Rule cache cleared")


class RuleEvaluationError(Exception):
    """Raised when rule evaluation fails"""
    pass


# ============================================================================
# MOCK ENGINE (For development/testing without GoRules installed)
# ============================================================================

class MockRuleEngineService(RuleEngineService):
    """
    Mock rule engine for testing without GoRules dependency
    
    Returns hardcoded decisions based on simple logic.
    """
    
    def __init__(self, rules_directory: str = "rules"):
        # Don't initialize real engine
        self.rules_directory = Path(rules_directory)
        self._rule_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("MockRuleEngineService initialized (no real engine)")
    
    def evaluate(
        self,
        rule_path: str,
        facts: Dict[str, Any],
        trace: bool = False,
    ) -> Dict[str, Any]:
        """
        Mock evaluation with simple hardcoded logic
        """
        logger.info(f"Mock evaluation: {rule_path}")
        
        # Simple mock logic for KYC eligibility
        if "pan_verification_status" in facts:
            if facts["pan_verification_status"] != "VERIFIED":
                return {
                    "kyc_eligibility_status": "REJECTED",
                    "kyc_rejection_reason": "PAN_INVALID",
                    "_metadata": {
                        "rule_path": rule_path,
                        "execution_time_ms": 5.0,
                        "evaluation_timestamp": datetime.utcnow().isoformat(),
                    }
                }
            
            if facts.get("customer_age", 0) < 21:
                return {
                    "kyc_eligibility_status": "REJECTED",
                    "kyc_rejection_reason": "AGE_BELOW_THRESHOLD",
                    "_metadata": {
                        "rule_path": rule_path,
                        "execution_time_ms": 5.0,
                        "evaluation_timestamp": datetime.utcnow().isoformat(),
                    }
                }
            
            if facts.get("dedupe_match_found", False):
                return {
                    "kyc_eligibility_status": "REJECTED",
                    "kyc_rejection_reason": "DUPLICATE_CUSTOMER",
                    "_metadata": {
                        "rule_path": rule_path,
                        "execution_time_ms": 5.0,
                        "evaluation_timestamp": datetime.utcnow().isoformat(),
                    }
                }
            
            cibil_score = facts.get("cibil_score")
            if cibil_score and cibil_score < 650:
                return {
                    "kyc_eligibility_status": "REJECTED",
                    "kyc_rejection_reason": "CIBIL_SCORE_LOW",
                    "_metadata": {
                        "rule_path": rule_path,
                        "execution_time_ms": 5.0,
                        "evaluation_timestamp": datetime.utcnow().isoformat(),
                    }
                }
            
            # Default: approved
            return {
                "kyc_eligibility_status": "APPROVED",
                "kyc_rejection_reason": None,
                "_metadata": {
                    "rule_path": rule_path,
                    "execution_time_ms": 5.0,
                    "evaluation_timestamp": datetime.utcnow().isoformat(),
                }
            }
        
        return {
            "error": "Unknown rule",
            "_metadata": {
                "rule_path": rule_path,
                "execution_time_ms": 1.0,
                "evaluation_timestamp": datetime.utcnow().isoformat(),
            }
        }

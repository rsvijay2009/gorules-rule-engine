"""
Audit Service for Decision Logging

CRITICAL REQUIREMENTS:
1. Log every decision with complete fact snapshot
2. Include rule version and execution metadata
3. Support regulatory audit requirements
4. Async writes (non-blocking)
5. Structured logging for analysis
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
import json

from pydantic import BaseModel


logger = logging.getLogger(__name__)


# ============================================================================
# AUDIT LOG MODELS
# ============================================================================

class DecisionAuditLog(BaseModel):
    """
    Complete audit log for a decision
    
    This captures everything needed for regulatory compliance:
    - What facts were used (snapshot)
    - Which rule version was executed
    - What decision was made
    - When and by whom
    """
    
    # Request identifiers
    correlation_id: str
    request_timestamp: datetime
    
    # Rule execution metadata
    rule_path: str
    rule_version: Optional[str] = None
    execution_time_ms: float
    
    # Input facts (complete snapshot)
    input_facts: Dict[str, Any]
    fact_model_version: str  # e.g., "v1"
    
    # Decision output
    decision_output: Dict[str, Any]
    
    # Metadata
    service_name: str = "bre-platform"
    environment: str = "production"
    
    # Optional: User context (if available)
    user_id: Optional[str] = None
    client_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "request_timestamp": "2026-01-14T15:30:00Z",
                "rule_path": "kyc/pan_eligibility_v1.json",
                "rule_version": "v1.2.3",
                "execution_time_ms": 8.5,
                "input_facts": {
                    "pan_number": "ABCDE1234F",
                    "customer_age": 32,
                    "cibil_score": 750
                },
                "fact_model_version": "v1",
                "decision_output": {
                    "kyc_eligibility_status": "APPROVED"
                },
                "service_name": "bre-platform",
                "environment": "production"
            }
        }


class RuleChangeAuditLog(BaseModel):
    """
    Audit log for rule changes
    
    Captures who changed what rule, when, and why.
    """
    
    change_id: str
    timestamp: datetime
    
    # Who
    user_id: str
    user_email: str
    
    # What
    rule_path: str
    change_type: str  # "CREATE", "UPDATE", "DELETE", "ACTIVATE", "DEACTIVATE"
    old_version: Optional[str] = None
    new_version: str
    
    # Why
    change_reason: str
    ticket_id: Optional[str] = None  # JIRA, etc.
    
    # Diff (optional)
    diff: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "change_id": "chg-12345",
                "timestamp": "2026-01-14T10:00:00Z",
                "user_id": "user123",
                "user_email": "risk.analyst@company.com",
                "rule_path": "kyc/pan_eligibility_v1.json",
                "change_type": "UPDATE",
                "old_version": "v1.2.2",
                "new_version": "v1.2.3",
                "change_reason": "Updated CIBIL threshold from 600 to 650",
                "ticket_id": "RISK-456"
            }
        }


# ============================================================================
# AUDIT SERVICE
# ============================================================================

class AuditService:
    """
    Service for logging decisions and rule changes
    
    In production, this would write to:
    - Database (PostgreSQL, MongoDB)
    - Event stream (Kafka, Kinesis)
    - Log aggregation (ELK, Splunk, Datadog)
    
    For this implementation, we use structured logging.
    """
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.audit_logger = logging.getLogger("audit")
        
        # Configure structured logging
        self.audit_logger.setLevel(logging.INFO)
        
        logger.info(f"AuditService initialized for environment={environment}")
    
    async def log_decision(
        self,
        correlation_id: str,
        rule_path: str,
        input_facts: Dict[str, Any],
        decision_output: Dict[str, Any],
        execution_time_ms: float,
        fact_model_version: str = "v1",
        rule_version: Optional[str] = None,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
    ) -> None:
        """
        Log a decision audit entry
        
        This is async to avoid blocking the request.
        """
        try:
            audit_log = DecisionAuditLog(
                correlation_id=correlation_id,
                request_timestamp=datetime.utcnow(),
                rule_path=rule_path,
                rule_version=rule_version,
                execution_time_ms=execution_time_ms,
                input_facts=input_facts,
                fact_model_version=fact_model_version,
                decision_output=decision_output,
                environment=self.environment,
                user_id=user_id,
                client_id=client_id,
            )
            
            # Structured log
            self.audit_logger.info(
                "DECISION_AUDIT",
                extra={
                    "audit_type": "decision",
                    "correlation_id": correlation_id,
                    "rule_path": rule_path,
                    "decision_status": decision_output.get("kyc_eligibility_status"),
                    "execution_time_ms": execution_time_ms,
                    "audit_log": audit_log.model_dump(),
                }
            )
            
            # In production, also write to database/event stream
            # await self._write_to_database(audit_log)
            # await self._publish_to_event_stream(audit_log)
            
        except Exception as e:
            # Never fail the request due to audit logging failure
            logger.error(f"Failed to log decision audit: {e}")
    
    async def log_rule_change(
        self,
        user_id: str,
        user_email: str,
        rule_path: str,
        change_type: str,
        new_version: str,
        change_reason: str,
        old_version: Optional[str] = None,
        ticket_id: Optional[str] = None,
        diff: Optional[str] = None,
    ) -> None:
        """
        Log a rule change audit entry
        """
        try:
            change_log = RuleChangeAuditLog(
                change_id=f"chg-{datetime.utcnow().timestamp()}",
                timestamp=datetime.utcnow(),
                user_id=user_id,
                user_email=user_email,
                rule_path=rule_path,
                change_type=change_type,
                old_version=old_version,
                new_version=new_version,
                change_reason=change_reason,
                ticket_id=ticket_id,
                diff=diff,
            )
            
            # Structured log
            self.audit_logger.info(
                "RULE_CHANGE_AUDIT",
                extra={
                    "audit_type": "rule_change",
                    "rule_path": rule_path,
                    "change_type": change_type,
                    "user_email": user_email,
                    "audit_log": change_log.model_dump(),
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to log rule change audit: {e}")
    
    def query_decision_history(
        self,
        correlation_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[DecisionAuditLog]:
        """
        Query decision audit history
        
        In production, this would query the database.
        For this implementation, it's a placeholder.
        """
        # Placeholder - would query database
        logger.info(
            f"Querying decision history: correlation_id={correlation_id}, "
            f"start={start_date}, end={end_date}, limit={limit}"
        )
        return []


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Global audit service instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get or create audit service singleton"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service

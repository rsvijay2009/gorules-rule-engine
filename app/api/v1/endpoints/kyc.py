"""
KYC Decision Endpoint

Domain-specific endpoint for KYC eligibility decisions.

CRITICAL PRINCIPLES:
1. No business logic in controllers
2. Stateless request handling
3. Correlation ID propagation
4. Comprehensive audit logging
5. Graceful error handling
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4
import logging
from app.core.config import settings

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.decisions import (
    KYCDecisionRequest,
    KYCDecisionResponse,
    ErrorResponse,
)
from app.adapters.kyc_adapter import (
    KYCFactAdapter,
    KarzaPANResponseDTO,
    CustomerServiceDTO,
    CIBILServiceDTO,
    DedupeServiceDTO,
)
from app.services.rule_engine import MockRuleEngineService, RuleEvaluationError
from app.services.audit import get_audit_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/decisions/kyc", tags=["KYC Decisions"])

# Initialize services
rule_engine = MockRuleEngineService(rules_directory=settings.RULES_DIR)  # Use MockRuleEngineService for demo
audit_service = get_audit_service()


@router.post(
    "/eligibility",
    response_model=KYCDecisionResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Evaluate KYC Eligibility",
    description="""
    Evaluate KYC eligibility for a customer based on PAN verification,
    demographics, credit score, and fraud checks.
    
    This endpoint:
    1. Adapts request to canonical facts
    2. Evaluates GoRules decision
    3. Logs decision for audit
    4. Returns decision response
    """,
)
async def evaluate_kyc_eligibility(
    request: KYCDecisionRequest,
) -> KYCDecisionResponse:
    """
    Evaluate KYC eligibility decision
    """
    
    # Generate correlation ID if not provided
    correlation_id = request.correlation_id or str(uuid4())
    
    logger.info(
        f"KYC eligibility request received",
        extra={
            "correlation_id": correlation_id,
            "pan_number": request.pan_number[:4] + "****",  # Masked for security
        }
    )
    
    try:
        # Step 1: Adapt request to canonical facts
        # In production, these DTOs would come from upstream services
        # For this demo, we construct them from the request
        
        karza_dto = KarzaPANResponseDTO(
            pan=request.pan_number,
            status=request.pan_verification_status.lower(),
            name_on_pan="Customer Name",  # Would come from Karza
            name_match_percentage=request.pan_name_match_score * 100,
        )
        
        customer_dto = CustomerServiceDTO(
            customer_id="cust-123",  # Would come from customer service
            date_of_birth="1992-01-01",  # Calculated from age
            state_code=request.customer_state[:2] if len(request.customer_state) > 2 else request.customer_state,
            segment=request.customer_type.lower(),
        )
        
        cibil_dto = CIBILServiceDTO(
            score=request.cibil_score,
            status_code="200" if request.cibil_fetch_status == "SUCCESS" else "404",
        )
        
        dedupe_dto = DedupeServiceDTO(
            is_duplicate=request.dedupe_match_found,
            match_score=request.dedupe_match_confidence * 100 if request.dedupe_match_confidence else None,
        )
        
        # Adapt to canonical facts
        canonical_facts = KYCFactAdapter.adapt(
            karza_response=karza_dto,
            customer_data=customer_dto,
            cibil_response=cibil_dto,
            dedupe_response=dedupe_dto,
            correlation_id=correlation_id,
        )
        
        logger.info(
            f"Facts adapted successfully",
            extra={"correlation_id": correlation_id}
        )
        
        # Step 2: Evaluate rule
        rule_path = "kyc/pan_eligibility_v1.json"
        
        decision_result = rule_engine.evaluate(
            rule_path=rule_path,
            facts=canonical_facts.model_dump(),
        )
        
        logger.info(
            f"Rule evaluated: {decision_result.get('kyc_eligibility_status')}",
            extra={
                "correlation_id": correlation_id,
                "decision": decision_result.get("kyc_eligibility_status"),
            }
        )
        
        # Step 3: Log decision for audit
        await audit_service.log_decision(
            correlation_id=correlation_id,
            rule_path=rule_path,
            input_facts=canonical_facts.model_dump(),
            decision_output=decision_result,
            execution_time_ms=decision_result.get("_metadata", {}).get("execution_time_ms", 0),
            fact_model_version="v1",
        )
        
        # Step 4: Return response
        response = KYCDecisionResponse(
            kyc_eligibility_status=decision_result["kyc_eligibility_status"],
            kyc_rejection_reason=decision_result.get("kyc_rejection_reason"),
            correlation_id=correlation_id,
            rule_version=decision_result.get("_metadata", {}).get("rule_path"),
            execution_time_ms=decision_result.get("_metadata", {}).get("execution_time_ms", 0),
            timestamp=datetime.utcnow(),
        )
        
        return response
        
    except ValueError as e:
        logger.error(
            f"Validation error: {e}",
            extra={"correlation_id": correlation_id}
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "VALIDATION_ERROR",
                "message": str(e),
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    
    except RuleEvaluationError as e:
        logger.error(
            f"Rule evaluation error: {e}",
            extra={"correlation_id": correlation_id}
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "RULE_EVALUATION_ERROR",
                "message": str(e),
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    
    except Exception as e:
        logger.error(
            f"Unexpected error: {e}",
            extra={"correlation_id": correlation_id},
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

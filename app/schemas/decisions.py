"""
API Schemas for Decision Gateway

Request/Response contracts for decision endpoints.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# KYC DECISION REQUEST/RESPONSE
# ============================================================================

class KYCDecisionRequest(BaseModel):
    """
    Request to evaluate KYC eligibility
    
    This is the external API contract. The Fact Adapter will map this
    to canonical facts internally.
    """
    
    # PAN data
    pan_number: str = Field(..., description="Customer's PAN number")
    pan_verification_status: str = Field(..., description="PAN verification status from Karza")
    pan_name_match_score: float = Field(..., ge=0.0, le=1.0, description="Name match score")
    
    # Customer data
    customer_age: int = Field(..., ge=18, description="Customer age")
    customer_state: str = Field(..., description="Customer state code")
    customer_type: str = Field(..., description="Customer type/segment")
    
    # Credit data
    cibil_score: Optional[int] = Field(None, ge=300, le=900, description="CIBIL score")
    cibil_fetch_status: str = Field(..., description="CIBIL fetch status")
    
    # Fraud data
    dedupe_match_found: bool = Field(default=False, description="Duplicate customer found")
    dedupe_match_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Optional metadata
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pan_number": "ABCDE1234F",
                "pan_verification_status": "VERIFIED",
                "pan_name_match_score": 0.95,
                "customer_age": 32,
                "customer_state": "KARNATAKA",
                "customer_type": "RETAIL",
                "cibil_score": 750,
                "cibil_fetch_status": "SUCCESS",
                "dedupe_match_found": False,
                "dedupe_match_confidence": None,
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class KYCDecisionResponse(BaseModel):
    """
    Response from KYC eligibility decision
    """
    
    # Decision output
    kyc_eligibility_status: str = Field(..., description="Final KYC decision")
    kyc_rejection_reason: Optional[str] = Field(None, description="Rejection reason if rejected")
    
    # Metadata
    correlation_id: str = Field(..., description="Request correlation ID")
    rule_version: Optional[str] = Field(None, description="Rule version used")
    execution_time_ms: float = Field(..., description="Rule execution time in milliseconds")
    timestamp: datetime = Field(..., description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kyc_eligibility_status": "APPROVED",
                "kyc_rejection_reason": None,
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "rule_version": "v1.2.3",
                "execution_time_ms": 8.5,
                "timestamp": "2026-01-14T15:30:01Z"
            }
        }


# ============================================================================
# GENERIC DECISION REQUEST/RESPONSE
# ============================================================================

class GenericDecisionRequest(BaseModel):
    """
    Generic decision request for any rule
    
    Allows clients to pass arbitrary facts as a dictionary.
    """
    
    rule_path: str = Field(..., description="Path to rule to evaluate")
    facts: Dict[str, Any] = Field(..., description="Input facts")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "rule_path": "kyc/pan_eligibility_v1.json",
                "facts": {
                    "pan_number": "ABCDE1234F",
                    "customer_age": 32
                },
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class GenericDecisionResponse(BaseModel):
    """
    Generic decision response
    """
    
    result: Dict[str, Any] = Field(..., description="Decision output")
    correlation_id: str = Field(..., description="Request correlation ID")
    execution_time_ms: float = Field(..., description="Execution time")
    timestamp: datetime = Field(..., description="Response timestamp")


# ============================================================================
# ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Standard error response
    """
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Invalid PAN format",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-01-14T15:30:01Z"
            }
        }


# ============================================================================
# HEALTH CHECK
# ============================================================================

class HealthCheckResponse(BaseModel):
    """
    Health check response
    """
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2026-01-14T15:30:01Z"
            }
        }

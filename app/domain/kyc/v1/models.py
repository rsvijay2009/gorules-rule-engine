"""
Canonical Fact Models for KYC Domain (Version 1)

These models represent the CANONICAL facts consumed by GoRules.
They are NEVER the same as backend DTOs - the Fact Adapter maps between them.

Key Principles:
1. Versioned (v1, v2, etc.) - allows backward-compatible evolution
2. Strongly typed using Pydantic
3. Aligned with Fact Registry definitions
4. Immutable after creation (frozen=True for production use)
5. No business logic - pure data models
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


# ============================================================================
# ENUMS (Must match Fact Registry allowed_values)
# ============================================================================

class PANVerificationStatus(str, Enum):
    """PAN verification status from external vendor"""
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    INVALID = "INVALID"
    PENDING = "PENDING"
    ERROR = "ERROR"


class CustomerState(str, Enum):
    """Indian states"""
    ANDHRA_PRADESH = "ANDHRA_PRADESH"
    KARNATAKA = "KARNATAKA"
    MAHARASHTRA = "MAHARASHTRA"
    TAMIL_NADU = "TAMIL_NADU"
    DELHI = "DELHI"
    WEST_BENGAL = "WEST_BENGAL"
    GUJARAT = "GUJARAT"
    RAJASTHAN = "RAJASTHAN"
    UTTAR_PRADESH = "UTTAR_PRADESH"
    TELANGANA = "TELANGANA"
    OTHER = "OTHER"


class CustomerType(str, Enum):
    """Customer classification"""
    RETAIL = "RETAIL"
    PREMIUM = "PREMIUM"
    CORPORATE = "CORPORATE"
    GOVERNMENT = "GOVERNMENT"


class CIBILFetchStatus(str, Enum):
    """CIBIL score fetch status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    NO_HISTORY = "NO_HISTORY"
    TIMEOUT = "TIMEOUT"


class KYCEligibilityStatus(str, Enum):
    """Final KYC decision output"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    PENDING_DOCUMENTS = "PENDING_DOCUMENTS"


class KYCRejectionReason(str, Enum):
    """KYC rejection reason codes"""
    PAN_INVALID = "PAN_INVALID"
    PAN_NAME_MISMATCH = "PAN_NAME_MISMATCH"
    AGE_BELOW_THRESHOLD = "AGE_BELOW_THRESHOLD"
    CIBIL_SCORE_LOW = "CIBIL_SCORE_LOW"
    DUPLICATE_CUSTOMER = "DUPLICATE_CUSTOMER"
    RESTRICTED_STATE = "RESTRICTED_STATE"
    INCOMPLETE_DOCUMENTS = "INCOMPLETE_DOCUMENTS"


# ============================================================================
# CANONICAL FACT MODEL (Input to Rules)
# ============================================================================

class KYCFactsV1(BaseModel):
    """
    Canonical fact model for KYC decision rules (Version 1)
    
    This is the ONLY model that GoRules sees. Backend DTOs are mapped to this
    by the Fact Adapter (Anti-Corruption Layer).
    
    All fields are validated against Fact Registry constraints.
    """
    
    # PAN Facts
    pan_number: str = Field(
        ...,
        description="Permanent Account Number",
        pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        min_length=10,
        max_length=10
    )
    pan_verification_status: PANVerificationStatus = Field(
        default=PANVerificationStatus.PENDING,
        description="PAN verification status from Karza"
    )
    pan_name_match_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fuzzy match score between PAN name and customer name"
    )
    
    # Customer Demographics
    customer_age: int = Field(
        ...,
        ge=18,
        le=120,
        description="Customer age in years"
    )
    customer_state: CustomerState = Field(
        ...,
        description="Customer's state of residence"
    )
    customer_type: CustomerType = Field(
        ...,
        description="Customer classification"
    )
    
    # Credit Bureau Facts
    cibil_score: Optional[int] = Field(
        None,
        ge=300,
        le=900,
        description="CIBIL credit score (300-900)"
    )
    cibil_fetch_status: CIBILFetchStatus = Field(
        ...,
        description="Status of CIBIL fetch operation"
    )
    
    # Dedupe / Fraud Facts
    dedupe_match_found: bool = Field(
        default=False,
        description="Whether duplicate customer record exists"
    )
    dedupe_match_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score of dedupe match"
    )
    
    # Audit Metadata
    correlation_id: str = Field(
        ...,
        description="Unique request identifier for tracing"
    )
    request_timestamp: datetime = Field(
        ...,
        description="Request timestamp (ISO 8601)"
    )
    
    @field_validator('correlation_id')
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        """Validate UUID format for correlation_id"""
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError(f"Invalid correlation_id format: {v}")
        return v.lower()
    
    class Config:
        # For production, consider frozen=True to make immutable
        # frozen = True
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
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "request_timestamp": "2026-01-14T15:30:00Z"
            }
        }


# ============================================================================
# CANONICAL DECISION OUTPUT MODEL
# ============================================================================

class KYCDecisionOutputV1(BaseModel):
    """
    Canonical decision output from KYC rules (Version 1)
    
    This is what GoRules returns after evaluation.
    """
    
    kyc_eligibility_status: KYCEligibilityStatus = Field(
        ...,
        description="Final KYC eligibility decision"
    )
    kyc_rejection_reason: Optional[KYCRejectionReason] = Field(
        None,
        description="Reason code if rejected"
    )
    
    # Rule execution metadata (added by engine)
    rule_version: Optional[str] = Field(
        None,
        description="Version of the rule that was executed"
    )
    evaluation_timestamp: Optional[datetime] = Field(
        None,
        description="When the rule was evaluated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "kyc_eligibility_status": "APPROVED",
                "kyc_rejection_reason": None,
                "rule_version": "v1.2.3",
                "evaluation_timestamp": "2026-01-14T15:30:01Z"
            }
        }


# ============================================================================
# VERSION REGISTRY
# ============================================================================

class KYCFactModelVersion(str, Enum):
    """Registry of KYC fact model versions"""
    V1 = "v1"
    # V2 = "v2"  # Future versions


# Mapping of version to model class
KYC_FACT_MODELS = {
    KYCFactModelVersion.V1: KYCFactsV1,
}

KYC_OUTPUT_MODELS = {
    KYCFactModelVersion.V1: KYCDecisionOutputV1,
}

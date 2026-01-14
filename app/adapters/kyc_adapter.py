"""
Fact Adapter (Anti-Corruption Layer) for KYC Domain

CRITICAL RESPONSIBILITIES:
1. Map backend DTOs → Canonical Fact Models
2. Normalize data (casing, enums, nulls, defaults)
3. Validate against Fact Registry constraints
4. Guarantee rule-safe input (no runtime failures)
5. Handle missing/malformed data gracefully

ANTI-PATTERNS TO AVOID:
- Never pass raw backend DTOs to rules
- Never allow free-text values for enum fields
- Never skip validation
- Never expose backend implementation details to rules
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4
import logging

from pydantic import BaseModel, ValidationError

from app.domain.kyc.v1 import (
    KYCFactsV1,
    PANVerificationStatus,
    CustomerState,
    CustomerType,
    CIBILFetchStatus,
)


logger = logging.getLogger(__name__)


# ============================================================================
# BACKEND DTOs (Examples - these come from upstream services)
# ============================================================================

class KarzaPANResponseDTO(BaseModel):
    """Example DTO from Karza PAN verification API"""
    pan: str
    status: str  # "valid", "invalid", "error" - NOT aligned with our enums
    name_on_pan: str
    name_match_percentage: float  # 0-100 scale, not 0-1


class CustomerServiceDTO(BaseModel):
    """Example DTO from internal customer service"""
    customer_id: str
    date_of_birth: str  # "YYYY-MM-DD" format
    state_code: str  # "KA", "MH" - NOT aligned with our enums
    segment: str  # "retail", "premium" - lowercase, not aligned


class CIBILServiceDTO(BaseModel):
    """Example DTO from CIBIL API"""
    score: Optional[int] = None
    status_code: str  # "200", "404", "500" - HTTP codes, not semantic
    error_message: Optional[str] = None


class DedupeServiceDTO(BaseModel):
    """Example DTO from dedupe service"""
    is_duplicate: bool
    match_score: Optional[float] = None  # 0-100 scale


# ============================================================================
# FACT ADAPTER
# ============================================================================

class KYCFactAdapter:
    """
    Anti-Corruption Layer for KYC domain
    
    Maps backend DTOs to KYCFactsV1 canonical model.
    Handles all normalization, validation, and error recovery.
    """
    
    # Mapping tables for normalization
    KARZA_STATUS_MAP = {
        "valid": PANVerificationStatus.VERIFIED,
        "invalid": PANVerificationStatus.INVALID,
        "pending": PANVerificationStatus.PENDING,
        "error": PANVerificationStatus.ERROR,
    }
    
    STATE_CODE_MAP = {
        "AP": CustomerState.ANDHRA_PRADESH,
        "KA": CustomerState.KARNATAKA,
        "MH": CustomerState.MAHARASHTRA,
        "TN": CustomerState.TAMIL_NADU,
        "DL": CustomerState.DELHI,
        "WB": CustomerState.WEST_BENGAL,
        "GJ": CustomerState.GUJARAT,
        "RJ": CustomerState.RAJASTHAN,
        "UP": CustomerState.UTTAR_PRADESH,
        "TG": CustomerState.TELANGANA,
    }
    
    CUSTOMER_SEGMENT_MAP = {
        "retail": CustomerType.RETAIL,
        "premium": CustomerType.PREMIUM,
        "corporate": CustomerType.CORPORATE,
        "government": CustomerType.GOVERNMENT,
    }
    
    CIBIL_STATUS_MAP = {
        "200": CIBILFetchStatus.SUCCESS,
        "404": CIBILFetchStatus.NO_HISTORY,
        "500": CIBILFetchStatus.FAILURE,
        "timeout": CIBILFetchStatus.TIMEOUT,
    }
    
    @staticmethod
    def adapt(
        karza_response: KarzaPANResponseDTO,
        customer_data: CustomerServiceDTO,
        cibil_response: CIBILServiceDTO,
        dedupe_response: DedupeServiceDTO,
        correlation_id: Optional[str] = None,
    ) -> KYCFactsV1:
        """
        Adapt backend DTOs to canonical KYC facts
        
        Args:
            karza_response: PAN verification response from Karza
            customer_data: Customer demographic data
            cibil_response: CIBIL score response
            dedupe_response: Dedupe check response
            correlation_id: Optional correlation ID (generated if not provided)
            
        Returns:
            KYCFactsV1: Validated canonical fact model
            
        Raises:
            ValueError: If adaptation fails due to invalid data
        """
        try:
            # Generate correlation ID if not provided
            if correlation_id is None:
                correlation_id = str(uuid4())
            
            # Normalize PAN verification status
            pan_status_raw = karza_response.status.lower()
            pan_verification_status = KYCFactAdapter.KARZA_STATUS_MAP.get(
                pan_status_raw,
                PANVerificationStatus.ERROR  # Default fallback
            )
            
            # Normalize PAN name match score (100 scale → 0-1 scale)
            pan_name_match_score = min(
                max(karza_response.name_match_percentage / 100.0, 0.0),
                1.0
            )
            
            # Calculate customer age from DOB
            dob = datetime.strptime(customer_data.date_of_birth, "%Y-%m-%d")
            today = datetime.now()
            customer_age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
            
            # Normalize customer state
            customer_state = KYCFactAdapter.STATE_CODE_MAP.get(
                customer_data.state_code.upper(),
                CustomerState.OTHER  # Default fallback
            )
            
            # Normalize customer type
            customer_type = KYCFactAdapter.CUSTOMER_SEGMENT_MAP.get(
                customer_data.segment.lower(),
                CustomerType.RETAIL  # Default fallback
            )
            
            # Normalize CIBIL status
            cibil_fetch_status = KYCFactAdapter.CIBIL_STATUS_MAP.get(
                cibil_response.status_code,
                CIBILFetchStatus.FAILURE  # Default fallback
            )
            
            # Normalize dedupe match confidence (100 scale → 0-1 scale)
            dedupe_match_confidence = None
            if dedupe_response.match_score is not None:
                dedupe_match_confidence = min(
                    max(dedupe_response.match_score / 100.0, 0.0),
                    1.0
                )
            
            # Construct canonical fact model
            canonical_facts = KYCFactsV1(
                pan_number=karza_response.pan.upper(),  # Normalize to uppercase
                pan_verification_status=pan_verification_status,
                pan_name_match_score=pan_name_match_score,
                customer_age=customer_age,
                customer_state=customer_state,
                customer_type=customer_type,
                cibil_score=cibil_response.score,
                cibil_fetch_status=cibil_fetch_status,
                dedupe_match_found=dedupe_response.is_duplicate,
                dedupe_match_confidence=dedupe_match_confidence,
                correlation_id=correlation_id,
                request_timestamp=datetime.utcnow(),
            )
            
            logger.info(
                f"Successfully adapted facts for correlation_id={correlation_id}",
                extra={
                    "correlation_id": correlation_id,
                    "pan_status": pan_verification_status.value,
                    "customer_age": customer_age,
                }
            )
            
            return canonical_facts
            
        except ValidationError as e:
            logger.error(
                f"Fact validation failed: {e}",
                extra={"correlation_id": correlation_id}
            )
            raise ValueError(f"Invalid fact data: {e}") from e
        except Exception as e:
            logger.error(
                f"Fact adaptation failed: {e}",
                extra={"correlation_id": correlation_id}
            )
            raise ValueError(f"Fact adaptation error: {e}") from e
    
    @staticmethod
    def adapt_from_dict(
        raw_data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> KYCFactsV1:
        """
        Convenience method to adapt from raw dictionary
        
        Useful for testing or when DTOs are not available.
        """
        try:
            # Parse DTOs from raw data
            karza_response = KarzaPANResponseDTO(**raw_data.get("karza", {}))
            customer_data = CustomerServiceDTO(**raw_data.get("customer", {}))
            cibil_response = CIBILServiceDTO(**raw_data.get("cibil", {}))
            dedupe_response = DedupeServiceDTO(**raw_data.get("dedupe", {}))
            
            return KYCFactAdapter.adapt(
                karza_response=karza_response,
                customer_data=customer_data,
                cibil_response=cibil_response,
                dedupe_response=dedupe_response,
                correlation_id=correlation_id,
            )
        except Exception as e:
            logger.error(f"Failed to adapt from dict: {e}")
            raise ValueError(f"Invalid raw data: {e}") from e


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class FactValidationError(Exception):
    """Raised when fact validation fails"""
    pass


def validate_facts_against_registry(facts: KYCFactsV1) -> None:
    """
    Additional validation against Fact Registry rules
    
    This is a placeholder for more sophisticated validation that could:
    - Check against fact registry lifecycle states
    - Validate deprecated facts are not used
    - Enforce additional business constraints
    """
    # Example: Check for deprecated facts (placeholder)
    # In production, this would load from fact_registry/facts/kyc_facts.yaml
    
    # Example: Validate PAN format
    if not facts.pan_number.isalnum():
        raise FactValidationError(f"Invalid PAN format: {facts.pan_number}")
    
    # Example: Validate age constraints
    if facts.customer_age < 18:
        raise FactValidationError(
            f"Customer age below minimum: {facts.customer_age}"
        )
    
    logger.debug(f"Fact validation passed for {facts.correlation_id}")

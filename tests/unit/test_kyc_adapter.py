"""
Unit tests for KYC Fact Adapter
"""

import pytest
from datetime import datetime
from uuid import uuid4

from app.adapters.kyc_adapter import (
    KYCFactAdapter,
    KarzaPANResponseDTO,
    CustomerServiceDTO,
    CIBILServiceDTO,
    DedupeServiceDTO,
    FactValidationError,
)
from app.domain.kyc.v1 import (
    PANVerificationStatus,
    CustomerState,
    CustomerType,
    CIBILFetchStatus,
)


class TestKYCFactAdapter:
    """Test suite for KYC Fact Adapter"""
    
    def test_successful_adaptation(self):
        """Test successful DTO to canonical facts adaptation"""
        # Arrange
        karza_dto = KarzaPANResponseDTO(
            pan="ABCDE1234F",
            status="valid",
            name_on_pan="John Doe",
            name_match_percentage=95.0,
        )
        
        customer_dto = CustomerServiceDTO(
            customer_id="cust-123",
            date_of_birth="1992-01-01",
            state_code="KA",
            segment="retail",
        )
        
        cibil_dto = CIBILServiceDTO(
            score=750,
            status_code="200",
        )
        
        dedupe_dto = DedupeServiceDTO(
            is_duplicate=False,
            match_score=None,
        )
        
        correlation_id = str(uuid4())
        
        # Act
        facts = KYCFactAdapter.adapt(
            karza_response=karza_dto,
            customer_data=customer_dto,
            cibil_response=cibil_dto,
            dedupe_response=dedupe_dto,
            correlation_id=correlation_id,
        )
        
        # Assert
        assert facts.pan_number == "ABCDE1234F"
        assert facts.pan_verification_status == PANVerificationStatus.VERIFIED
        assert facts.pan_name_match_score == 0.95
        assert facts.customer_age == 32  # Calculated from DOB
        assert facts.customer_state == CustomerState.KARNATAKA
        assert facts.customer_type == CustomerType.RETAIL
        assert facts.cibil_score == 750
        assert facts.cibil_fetch_status == CIBILFetchStatus.SUCCESS
        assert facts.dedupe_match_found is False
        assert facts.correlation_id == correlation_id
    
    def test_pan_status_normalization(self):
        """Test PAN status normalization from various formats"""
        test_cases = [
            ("valid", PANVerificationStatus.VERIFIED),
            ("invalid", PANVerificationStatus.INVALID),
            ("pending", PANVerificationStatus.PENDING),
            ("error", PANVerificationStatus.ERROR),
            ("unknown", PANVerificationStatus.ERROR),  # Default fallback
        ]
        
        for raw_status, expected_status in test_cases:
            karza_dto = KarzaPANResponseDTO(
                pan="ABCDE1234F",
                status=raw_status,
                name_on_pan="Test",
                name_match_percentage=90.0,
            )
            
            facts = KYCFactAdapter.adapt(
                karza_response=karza_dto,
                customer_data=self._get_default_customer_dto(),
                cibil_response=self._get_default_cibil_dto(),
                dedupe_response=self._get_default_dedupe_dto(),
            )
            
            assert facts.pan_verification_status == expected_status
    
    def test_name_match_score_normalization(self):
        """Test name match score conversion from 0-100 to 0-1 scale"""
        test_cases = [
            (100.0, 1.0),
            (95.0, 0.95),
            (50.0, 0.5),
            (0.0, 0.0),
            (150.0, 1.0),  # Clamped to max
            (-10.0, 0.0),  # Clamped to min
        ]
        
        for input_score, expected_score in test_cases:
            karza_dto = KarzaPANResponseDTO(
                pan="ABCDE1234F",
                status="valid",
                name_on_pan="Test",
                name_match_percentage=input_score,
            )
            
            facts = KYCFactAdapter.adapt(
                karza_response=karza_dto,
                customer_data=self._get_default_customer_dto(),
                cibil_response=self._get_default_cibil_dto(),
                dedupe_response=self._get_default_dedupe_dto(),
            )
            
            assert facts.pan_name_match_score == expected_score
    
    def test_state_code_mapping(self):
        """Test state code to enum mapping"""
        test_cases = [
            ("KA", CustomerState.KARNATAKA),
            ("MH", CustomerState.MAHARASHTRA),
            ("DL", CustomerState.DELHI),
            ("XX", CustomerState.OTHER),  # Unknown code
        ]
        
        for state_code, expected_state in test_cases:
            customer_dto = CustomerServiceDTO(
                customer_id="cust-123",
                date_of_birth="1992-01-01",
                state_code=state_code,
                segment="retail",
            )
            
            facts = KYCFactAdapter.adapt(
                karza_response=self._get_default_karza_dto(),
                customer_data=customer_dto,
                cibil_response=self._get_default_cibil_dto(),
                dedupe_response=self._get_default_dedupe_dto(),
            )
            
            assert facts.customer_state == expected_state
    
    def test_missing_cibil_score_handling(self):
        """Test handling of missing CIBIL score"""
        cibil_dto = CIBILServiceDTO(
            score=None,
            status_code="404",
        )
        
        facts = KYCFactAdapter.adapt(
            karza_response=self._get_default_karza_dto(),
            customer_data=self._get_default_customer_dto(),
            cibil_response=cibil_dto,
            dedupe_response=self._get_default_dedupe_dto(),
        )
        
        assert facts.cibil_score is None
        assert facts.cibil_fetch_status == CIBILFetchStatus.NO_HISTORY
    
    def test_correlation_id_generation(self):
        """Test automatic correlation ID generation"""
        facts = KYCFactAdapter.adapt(
            karza_response=self._get_default_karza_dto(),
            customer_data=self._get_default_customer_dto(),
            cibil_response=self._get_default_cibil_dto(),
            dedupe_response=self._get_default_dedupe_dto(),
            correlation_id=None,  # Not provided
        )
        
        # Should generate a valid UUID
        assert facts.correlation_id is not None
        assert len(facts.correlation_id) == 36  # UUID format
    
    # Helper methods
    
    def _get_default_karza_dto(self):
        return KarzaPANResponseDTO(
            pan="ABCDE1234F",
            status="valid",
            name_on_pan="Test User",
            name_match_percentage=90.0,
        )
    
    def _get_default_customer_dto(self):
        return CustomerServiceDTO(
            customer_id="cust-123",
            date_of_birth="1992-01-01",
            state_code="KA",
            segment="retail",
        )
    
    def _get_default_cibil_dto(self):
        return CIBILServiceDTO(
            score=700,
            status_code="200",
        )
    
    def _get_default_dedupe_dto(self):
        return DedupeServiceDTO(
            is_duplicate=False,
            match_score=None,
        )

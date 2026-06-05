import pytest
from datetime import date
from unittest.mock import MagicMock, patch

from app.models.member import Member
from app.schemas.extraction import ExtractionResult
from app.schemas.contracts import ClaimSubmitForm, AdjudicationResult
from app.services.adjudication_engine import (
    _check_eligibility,
    _check_documents,
    _check_coverage,
    _calculate_financials,
    _check_medical_necessity,
    _check_fraud,
    adjudicate
)


# Mock Member class for testing
class MockMember:
    def __init__(self, join_date, member_id="EMP123", name="Test Member"):
        self.member_id = member_id
        self.name = name
        self.join_date = join_date


def test_check_eligibility():
    # Joined today, treatment today (< 90 days)
    m1 = MockMember(join_date=date(2024, 1, 1))
    assert _check_eligibility(m1, date(2024, 2, 1)) == "WAITING_PERIOD"

    # Joined long ago (>= 90 days)
    m2 = MockMember(join_date=date(2024, 1, 1))
    assert _check_eligibility(m2, date(2024, 5, 1)) is None

    # Handle string dates safely
    m3 = MockMember(join_date="2024-01-01")
    assert _check_eligibility(m3, "2024-02-01") == "WAITING_PERIOD"
    assert _check_eligibility(m3, "2024-05-01") is None


def test_check_documents():
    # Missing prescription
    ext1 = ExtractionResult(has_prescription=False, doctor_registration="KA/45678/2015")
    assert _check_documents(ext1) == "MISSING_DOCUMENTS"

    # Missing doctor registration
    ext2 = ExtractionResult(has_prescription=True, doctor_registration=None)
    assert _check_documents(ext2) == "DOCTOR_REG_INVALID"

    # Invalid registration format
    ext3 = ExtractionResult(has_prescription=True, doctor_registration="INVALID-123")
    assert _check_documents(ext3) == "DOCTOR_REG_INVALID"

    # Valid registration formats
    ext4 = ExtractionResult(has_prescription=True, doctor_registration="KA/45678/2015")
    assert _check_documents(ext4) is None

    ext5 = ExtractionResult(has_prescription=True, doctor_registration="AYUR/KL/2345/2019")
    assert _check_documents(ext5) is None


def test_check_coverage():
    claim_req = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 1, 1),
        claim_amount=1500.0,
        pre_auth_provided=False
    )

    # Exclusions check: weight loss in diagnosis
    ext = ExtractionResult(diagnosis="Weight loss program", procedures=[])
    rejection_reasons, rejected_items = _check_coverage(ext, claim_req)
    assert "SERVICE_NOT_COVERED" in rejection_reasons
    assert len(rejected_items) == 0

    # Exclusions check: bariatric in procedures
    ext = ExtractionResult(diagnosis="Obesity", procedures=["Bariatric surgery"])
    rejection_reasons, rejected_items = _check_coverage(ext, claim_req)
    assert "SERVICE_NOT_COVERED" in rejection_reasons
    assert len(rejected_items) == 0

    # Cosmetic check
    ext = ExtractionResult(diagnosis="Dental cavity", procedures=["Teeth Whitening", "Filling"])
    rejection_reasons, rejected_items = _check_coverage(ext, claim_req)
    assert "COSMETIC_PROCEDURE" in rejection_reasons
    assert "Teeth Whitening" in rejected_items
    assert "Filling" not in rejected_items

    # Pre-auth check: MRI > 10000 and not pre-auth provided
    ext = ExtractionResult(diagnosis="Headache", procedures=["MRI brain"], diagnostic_cost=12000.0)
    rejection_reasons, rejected_items = _check_coverage(ext, claim_req)
    assert "PRE_AUTH_MISSING" in rejection_reasons

    # Pre-auth provided -> should not trigger PRE_AUTH_MISSING
    claim_req_auth = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 1, 1),
        claim_amount=1500.0,
        pre_auth_provided=True
    )
    rejection_reasons, rejected_items = _check_coverage(ext, claim_req_auth)
    assert "PRE_AUTH_MISSING" not in rejection_reasons


def test_calculate_financials():
    ext_standard = ExtractionResult(diagnosis="Viral fever", procedures=[], medicines=[])

    # Limit exceeded
    approved, deductions, reason = _calculate_financials(6000.0, None, [], ext_standard)
    assert reason == "PER_CLAIM_EXCEEDED"
    assert approved == 0.0

    # Non-network hospital -> 10% copay
    approved, deductions, reason = _calculate_financials(2000.0, "Random Clinic", [], ext_standard)
    assert reason is None
    assert approved == 1800.0
    assert deductions == {"copay": 200.0}

    # Network hospital -> 20% discount (e.g. Apollo Hospitals)
    approved, deductions, reason = _calculate_financials(2000.0, "Apollo Hospitals, Bangalore", [], ext_standard)
    assert reason is None
    assert approved == 1600.0
    assert deductions == {"network_discount": 400.0}

    # Dental claim under sub-limit (10000) — dental has zero copay
    ext_dental = ExtractionResult(diagnosis="Tooth decay", procedures=["Filling"], medicines=[])
    approved, deductions, reason = _calculate_financials(8000.0, "Random Clinic", [], ext_dental)
    assert reason is None
    assert approved == 8000.0
    assert deductions == {}

    # Dental claim exceeding sub-limit (10000)
    approved, deductions, reason = _calculate_financials(11000.0, "Random Clinic", [], ext_dental)
    assert reason == "PER_CLAIM_EXCEEDED"
    assert approved == 0.0

    # Dental exception & Cosmetic Deduction: 12000 claim with teeth whitening — dental has zero copay
    ext_dental_cosmetic = ExtractionResult(diagnosis="Tooth decay requiring root canal", procedures=["Root canal treatment", "Teeth whitening"], medicines=[])
    approved, deductions, reason = _calculate_financials(12000.0, "Random Clinic", ["Teeth whitening"], ext_dental_cosmetic)
    assert reason is None
    assert approved == 8000.0  # (12000 - 4000), zero copay for dental
    assert deductions == {}


@pytest.mark.asyncio
@patch("app.services.adjudication_engine._client")
async def test_check_medical_necessity(mock_client):
    ext = ExtractionResult(diagnosis="Viral fever", medicines=["Paracetamol"], procedures=[])

    # Model replies YES
    mock_resp_yes = MagicMock()
    mock_resp_yes.text = "YES"
    mock_client.models.generate_content.return_value = mock_resp_yes
    assert await _check_medical_necessity(ext) is None

    # Model replies NO
    mock_resp_no = MagicMock()
    mock_resp_no.text = "NO"
    mock_client.models.generate_content.return_value = mock_resp_no
    assert await _check_medical_necessity(ext) == "NOT_MEDICALLY_NECESSARY"

    # API fails -> fail open (returns None)
    mock_client.models.generate_content.side_effect = Exception("API Error")
    assert await _check_medical_necessity(ext) is None

    # Edge case: LLM responds with "NOT APPLICABLE" — should NOT reject
    mock_client.models.generate_content.side_effect = None
    mock_resp_edge = MagicMock()
    mock_resp_edge.text = "NOT APPLICABLE"
    mock_client.models.generate_content.return_value = mock_resp_edge
    assert await _check_medical_necessity(ext) is None

    # Edge case: LLM responds with "NO." (trailing punctuation) — should NOT reject
    mock_resp_dot = MagicMock()
    mock_resp_dot.text = "NO."
    mock_client.models.generate_content.return_value = mock_resp_dot
    assert await _check_medical_necessity(ext) is None

    # Edge case: empty diagnosis — should skip LLM call entirely
    ext_empty = ExtractionResult(diagnosis=None, medicines=["Paracetamol"], procedures=[])
    assert await _check_medical_necessity(ext_empty) is None


def test_check_fraud():
    ext = ExtractionResult()
    claim_req_normal = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 1, 1),
        claim_amount=1000.0,
        previous_claims_same_day=2
    )
    assert _check_fraud(claim_req_normal, ext) is None

    claim_req_fraud = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 1, 1),
        claim_amount=1000.0,
        previous_claims_same_day=3
    )
    assert _check_fraud(claim_req_fraud, ext) == "MANUAL_REVIEW"


@pytest.mark.asyncio
@patch("app.services.adjudication_engine._client")
async def test_adjudicate_approved(mock_client):
    # Setup mocks
    mock_resp = MagicMock()
    mock_resp.text = "YES"
    mock_client.models.generate_content.return_value = mock_resp

    member = MockMember(join_date=date(2023, 1, 1))
    claim_req = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 5, 1),
        claim_amount=2000.0,
        hospital_name="Apollo Hospitals"
    )
    extraction = ExtractionResult(
        doctor_name="Dr. Smith",
        doctor_registration="KA/45678/2015",
        diagnosis="Infection",
        medicines=["Antibiotics"],
        procedures=[],
        has_prescription=True,
        extraction_confidence=0.95
    )

    result = await adjudicate(claim_req, extraction, member)
    assert isinstance(result, AdjudicationResult)
    assert result.decision == "APPROVED"
    assert result.approved_amount == 1600.0
    assert result.deductions == {"network_discount": 400.0}
    assert result.rule_matrix == {
        "eligibility": "PASS",
        "documents": "PASS",
        "coverage": "PASS",
        "financials": "PASS",
        "necessity": "PASS",
        "fraud": "PASS"
    }
    assert result.confidence_score == 0.95


@pytest.mark.asyncio
@patch("app.services.adjudication_engine._client")
async def test_adjudicate_partial(mock_client):
    # Setup mocks
    mock_resp = MagicMock()
    mock_resp.text = "YES"
    mock_client.models.generate_content.return_value = mock_resp

    member = MockMember(join_date=date(2023, 1, 1))
    claim_req = ClaimSubmitForm(
        member_id="EMP001",
        treatment_date=date(2024, 5, 1),
        claim_amount=2000.0,
        hospital_name=None
    )
    extraction = ExtractionResult(
        doctor_name="Dr. Smith",
        doctor_registration="KA/45678/2015",
        diagnosis="Infection",
        medicines=["Antibiotics"],
        procedures=["Cosmetic Whitening"],
        has_prescription=True,
        extraction_confidence=0.9
    )

    result = await adjudicate(claim_req, extraction, member)
    assert isinstance(result, AdjudicationResult)
    assert result.decision == "PARTIAL"
    assert result.approved_amount == 1800.0
    assert result.deductions == {"copay": 200.0}
    assert "COSMETIC_PROCEDURE" in result.rejection_reasons
    assert "Cosmetic Whitening" in result.rejected_items
    assert result.rule_matrix == {
        "eligibility": "PASS",
        "documents": "PASS",
        "coverage": "PASS",
        "financials": "PASS",
        "necessity": "PASS",
        "fraud": "PASS"
    }

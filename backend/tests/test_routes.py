import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import date, datetime

from app.main import app
from app.database.connection import get_db
from app.models import Member, Claim
from app.schemas import ExtractionResult, AdjudicationResult

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert data["engine"] == "ClaimIQ Adjudication API"

def test_policy_endpoint():
    response = client.get("/api/policy")
    assert response.status_code == 200
    data = response.json()
    # It should load policy terms or return empty if file missing
    assert isinstance(data, dict)

def test_list_claims(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_count_result = MagicMock()
    mock_count_result.scalar_one.return_value = 1
    
    mock_list_result = MagicMock()
    mock_claim = Claim(
        claim_id="test-claim-uuid",
        member_id="EMP001",
        treatment_date=date(2024, 11, 1),
        submitted_amount=1500.0,
        hospital_name="Apollo Hospitals",
        decision="APPROVED",
        created_at=datetime(2024, 11, 1, 10, 0, 0)
    )
    mock_list_result.all.return_value = [(mock_claim, "Rajesh Kumar")]
    
    mock_db.execute.side_effect = [mock_count_result, mock_list_result]
    
    response = client.get("/api/claims/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["claims"]) == 1
    assert data["claims"][0]["claim_id"] == "test-claim-uuid"
    assert data["claims"][0]["member_name"] == "Rajesh Kumar"
    
    app.dependency_overrides.clear()

def test_get_claim_not_found(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_result = MagicMock()
    mock_result.one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/claims/non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Claim not found"
    
    app.dependency_overrides.clear()

def test_get_claim_success(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_result = MagicMock()
    mock_claim = Claim(
        claim_id="test-claim-uuid",
        member_id="EMP001",
        treatment_date=date(2024, 11, 1),
        submitted_amount=1500.0,
        decision="APPROVED",
        created_at=datetime(2024, 11, 1, 10, 0, 0)
    )
    mock_result.one_or_none.return_value = (mock_claim, "Rajesh Kumar")
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/claims/test-claim-uuid")
    assert response.status_code == 200
    data = response.json()
    assert data["claim_id"] == "test-claim-uuid"
    assert data["member_name"] == "Rajesh Kumar"
    
    app.dependency_overrides.clear()

@patch("app.routes.claims.process_documents")
@patch("app.routes.claims.extract_from_documents")
@patch("app.routes.claims.adjudicate")
def test_submit_claim_success(mock_adjudicate, mock_extract, mock_process_docs, mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    # 1. Mock member database query
    mock_member_res = MagicMock()
    mock_member = Member(member_id="EMP001", name="Rajesh Kumar", join_date=date(2023, 1, 1))
    mock_member_res.scalar_one_or_none.return_value = mock_member
    mock_db.execute.return_value = mock_member_res
    
    # 2. Mock process_documents
    mock_process_docs.return_value = {
        "base64_images": ["img1"],
        "ocr_text": "Sample prescription text"
    }
    
    # 3. Mock extract_from_documents
    mock_extract.return_value = ExtractionResult(
        doctor_name="Dr. Smith",
        doctor_registration="KA/45678/2015",
        has_prescription=True,
        extraction_confidence=0.9
    )
    
    # 4. Mock adjudicate
    mock_adjudicate.return_value = AdjudicationResult(
        decision="APPROVED",
        approved_amount=1350.0,
        deductions={"copay": 150.0},
        rule_matrix={"eligibility": "PASS"},
        notes="Claim approved successfully.",
        next_steps="None"
    )
    
    # Send request with multipart/form-data
    response = client.post(
        "/api/claims/",
        data={
            "member_id": "EMP001",
            "treatment_date": "2024-11-01",
            "claim_amount": "1500.0",
            "hospital_name": "Local Clinic",
            "cashless_request": "false",
            "pre_auth_provided": "false",
            "previous_claims_same_day": "0"
        },
        files=[("files", ("prescription.png", b"fake image content", "image/png"))]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "APPROVED"
    assert data["approved_amount"] == 1350.0
    assert data["member_name"] == "Rajesh Kumar"
    
    # Cleanup uploads
    upload_dir = os.path.join("uploads", data["claim_id"])
    if os.path.exists(upload_dir):
        import shutil
        shutil.rmtree(upload_dir)
        
    app.dependency_overrides.clear()

def test_get_stats(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    
    mock_result = MagicMock()
    mock_claim1 = Claim(
        claim_id="clm-1",
        member_id="EMP001",
        decision="APPROVED",
        approved_amount=1000.0,
        confidence_score=0.9
    )
    mock_claim2 = Claim(
        claim_id="clm-2",
        member_id="EMP002",
        decision="REJECTED",
        approved_amount=0.0,
        confidence_score=0.8
    )
    mock_result.scalars.return_value.all.return_value = [mock_claim1, mock_claim2]
    mock_db.execute.return_value = mock_result
    
    response = client.get("/api/claims/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["approved"] == 1
    assert data["rejected"] == 1
    assert data["total_approved_amount"] == 1000.0
    assert data["avg_confidence"] == pytest.approx(0.85)
    
    app.dependency_overrides.clear()


import pytest
from unittest.mock import MagicMock, patch
from app.schemas.extraction import ExtractionResult
from app.services.ai_extractor import _extract_sync, extract_from_documents


@pytest.mark.asyncio
async def test_extract_from_documents_empty_images():
    """Test that extract_from_documents returns a no_documents flag when base64_images list is empty."""
    result = await extract_from_documents([], "some text")
    assert result.extraction_confidence == 0.0
    assert "no_documents" in result.anomaly_flags


@patch("app.services.ai_extractor._client")
def test_extract_sync_success(mock_client):
    """Test that _extract_sync successfully calls Gemini and parses the response."""
    # Prepare a valid mock JSON response text
    mock_response_text = """
    {
        "doctor_name": "Dr. Sharma",
        "doctor_registration": "KA/45678/2015",
        "patient_name": "Rajesh Kumar",
        "patient_age": 35,
        "diagnosis": "Viral fever",
        "medicines": ["Paracetamol 650mg", "Vitamin C"],
        "procedures": [],
        "treatment_type": "allopathic",
        "consultation_fee": 1000.0,
        "medicine_cost": 0.0,
        "diagnostic_cost": 500.0,
        "total_amount": 1500.0,
        "treatment_date": "2024-11-01",
        "document_types_found": ["prescription", "bill"],
        "has_prescription": true,
        "extraction_confidence": 0.95,
        "anomaly_flags": []
    }
    """
    
    # Mock the API generate_content return value
    mock_response = MagicMock()
    mock_response.text = mock_response_text
    mock_client.models.generate_content.return_value = mock_response
    
    # Call sync extraction with dummy arguments
    result = _extract_sync(["dGVzdF9pbWFnZV9ieXRlcw=="], "OCR Text")
    
    # Assert result structure and values
    assert isinstance(result, ExtractionResult)
    assert result.doctor_name == "Dr. Sharma"
    assert result.doctor_registration == "KA/45678/2015"
    assert result.diagnosis == "Viral fever"
    assert result.has_prescription is True
    assert result.total_amount == 1500.0
    assert result.extraction_confidence == 0.95
    assert len(result.anomaly_flags) == 0

    # Ensure generate_content was called
    mock_client.models.generate_content.assert_called_once()


@patch("app.services.ai_extractor._client")
@patch("app.services.ai_extractor.time.sleep")  # Mock sleep to speed up test
def test_extract_sync_retry_and_failure(mock_sleep, mock_client):
    """Test that _extract_sync retries 3 times on API failure and falls back to failure result."""
    # Configure mock client to raise Exception on call
    mock_client.models.generate_content.side_effect = Exception("Gemini API Error")
    
    # Run sync extraction with dummy arguments
    result = _extract_sync(["dGVzdF9pbWFnZV9ieXRlcw=="], "OCR Text")
    
    # Assert fallback results
    assert isinstance(result, ExtractionResult)
    assert result.extraction_confidence == 0.0
    assert "extraction_failed" in result.anomaly_flags
    
    # Assert retry counts (1 initial + 2 retries = 3 calls total)
    assert mock_client.models.generate_content.call_count == 3
    # Assert sleep called twice (between 3 attempts)
    assert mock_sleep.call_count == 2
    mock_sleep.assert_called_with(2)

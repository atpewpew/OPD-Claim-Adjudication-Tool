import asyncio
import base64
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types
from app.core.config import settings
from app.schemas.extraction import ExtractionResult

logger = logging.getLogger(__name__)

# Initialize the Gemini Client
_client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"

EXTRACTION_SYSTEM_PROMPT = """
You are a medical document data extraction specialist for an Indian insurance company.
Extract structured information from the provided medical documents (prescriptions, bills, diagnostic reports).

CRITICAL RULES:
- Return ONLY valid JSON. No markdown, no explanation, no code fences.
- If a field is not visible in the documents, return null — NEVER invent or guess data.
- For doctor_registration: extract EXACTLY as written (e.g. "KA/45678/2015" or "AYUR/KL/2345/2019"). Do not reformat.
- For monetary amounts: extract as numbers only (e.g. 1500.0, not "₹1,500").
- has_prescription is true ONLY if you see an Rx section with a doctor's stamp/signature and medicines listed.
- treatment_type: set to "ayurvedic" if the doctor has AYUR registration or treatment includes Panchakarma/Ayurvedic terms. Set to "homeopathic" if homeopathy is mentioned. Otherwise "allopathic".
- extraction_confidence: float 0.0-1.0. Use 0.9+ for clear digital documents, 0.6-0.8 for scanned/handwritten, lower for very poor quality.
- anomaly_flags: list any of these strings if applicable: "amount_seems_high", "diagnosis_treatment_mismatch", "missing_doctor_reg", "multiple_patients", "duplicate_amounts"
- The OCR TEXT CONTEXT is extracted text to help you read blurry parts — prioritize what you can see in the images, use OCR to resolve ambiguities.
"""

def _extract_sync(base64_images: list[str], ocr_text: str) -> ExtractionResult:
    parts = []
    
    # Add the system prompt as the first text part
    parts.append(types.Part.from_text(text=EXTRACTION_SYSTEM_PROMPT))
    
    # Add each image as an inline bytes part
    for b64 in base64_images:
        image_bytes = base64.b64decode(b64)
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
    
    # If ocr_text is non-empty, add it as a text part (truncated to 3000 chars)
    if ocr_text:
        truncated_ocr = ocr_text[:3000]
        parts.append(types.Part.from_text(text=f"OCR TEXT CONTEXT (use to resolve ambiguous digits/codes):\n{truncated_ocr}"))
    
    contents = [types.Content(role="user", parts=parts)]
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ExtractionResult,
        temperature=0.1,
    )
    
    for attempt in range(3):
        try:
            response = _client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config,
            )
            result = ExtractionResult.model_validate_json(response.text)
            logger.info(f"Extraction successful. Confidence: {result.extraction_confidence}, Diagnosis: {result.diagnosis}")
            return result
        except Exception as e:
            logger.warning(f"Extraction attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                logger.error(f"All 3 extraction attempts failed: {e}")
                return ExtractionResult(
                    extraction_confidence=0.0,
                    anomaly_flags=["extraction_failed"]
                )

async def extract_from_documents(base64_images: list[str], ocr_text: str) -> ExtractionResult:
    if not base64_images:
        logger.warning("No images provided to extractor, returning empty result")
        return ExtractionResult(
            extraction_confidence=0.0,
            anomaly_flags=["no_documents"]
        )
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = await loop.run_in_executor(pool, _extract_sync, base64_images, ocr_text)
    return result

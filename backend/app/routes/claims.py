import os
import uuid
import shutil
import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.connection import get_db
from app.schemas import (
    ClaimResponse,
    ClaimsListResponse,
    ClaimSubmitForm,
    ExtractionResult,
    AdjudicationResult,
    StatsResponse
)
from app.models import Claim, Member
from app.services.document_pipeline import process_documents
from app.services.ai_extractor import extract_from_documents
from app.services.adjudication_engine import adjudicate

logger = logging.getLogger(__name__)
router = APIRouter()

def prepare_claim_response(claim: Claim, member_name: str) -> Claim:
    """
    Defensively prepares the Claim ORM object for Pydantic serialization.
    Fills in None values for lists/dicts and adds dynamic properties not stored as columns.
    """
    claim.member_name = member_name
    
    # Ensure created_at is populated
    if not claim.created_at:
        from datetime import datetime, UTC
        claim.created_at = datetime.now(UTC)
        
    # Standardize JSON/Nullable fields to prevent Pydantic validation errors
    if claim.rejection_reasons is None:
        claim.rejection_reasons = []
    if claim.rule_matrix is None:
        claim.rule_matrix = {}
    if claim.deductions is None:
        claim.deductions = {}
    if claim.document_urls is None:
        claim.document_urls = []
        
    # Dynamically bind rejected_items (expected by ClaimResponse but not in ORM schema)
    if not hasattr(claim, "rejected_items") or claim.rejected_items is None:
        claim.rejected_items = []
        
    return claim

@router.post("/", response_model=ClaimResponse)
async def submit_claim(
    member_id: str = Form(...),
    treatment_date: date = Form(...),
    claim_amount: float = Form(...),
    hospital_name: str | None = Form(None),
    cashless_request: bool = Form(False),
    pre_auth_provided: bool = Form(False),
    previous_claims_same_day: int = Form(0),
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new insurance claim with medical documents.
    """
    # 1. Fetch the Member from DB. Raise HTTPException 404 if not found.
    member_stmt = select(Member).where(Member.member_id == member_id)
    member_res = await db.execute(member_stmt)
    member = member_res.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # 2. Save uploaded files to local uploads directory
    claim_id = str(uuid.uuid4())
    upload_dir = os.path.join("uploads", claim_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_paths = []
    for file in files:
        if not file.filename:
            continue
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        file_paths.append(file_path)

    try:
        # 3. Process the documents to get OCR and images
        doc_result = process_documents(file_paths)

        # 4. Extract structured details from documents using Gemini
        extraction = await extract_from_documents(doc_result["base64_images"], doc_result["ocr_text"])

        # 5. Build ClaimSubmitForm schema
        claim_req = ClaimSubmitForm(
            member_id=member_id,
            treatment_date=treatment_date,
            claim_amount=claim_amount,
            hospital_name=hospital_name,
            cashless_request=cashless_request,
            pre_auth_provided=pre_auth_provided,
            previous_claims_same_day=previous_claims_same_day
        )

        # 6. Adjudicate the claim
        adjudication = await adjudicate(claim_req, extraction, member)

        # 7. Create a new Claim ORM object
        claim = Claim(
            claim_id=claim_id,
            member_id=member_id,
            treatment_date=treatment_date,
            submitted_amount=claim_amount,
            hospital_name=hospital_name,
            cashless_request=cashless_request,
            pre_auth_provided=pre_auth_provided,
            previous_claims_same_day=previous_claims_same_day,
            document_urls=file_paths,
            raw_ocr_text=doc_result["ocr_text"],
            extracted_data=extraction.model_dump(),
            decision=adjudication.decision,
            approved_amount=adjudication.approved_amount,
            rejection_reasons=adjudication.rejection_reasons,
            rule_matrix=adjudication.rule_matrix,
            deductions=adjudication.deductions,
            confidence_score=adjudication.confidence_score,
            notes=adjudication.notes,
            next_steps=adjudication.next_steps if hasattr(adjudication, "next_steps") else ""
        )

        # 8. Save claim to database
        db.add(claim)
        await db.commit()
        try:
            await db.refresh(claim)
        except Exception:
            pass

        # Populate rejected_items dynamically from adjudication
        claim.rejected_items = adjudication.rejected_items

        return prepare_claim_response(claim, member.name)

    except Exception as e:
        logger.error(f"Error submitting claim: {e}", exc_info=True)
        # Clean up files on error
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/", response_model=ClaimsListResponse)
async def list_claims(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all claims, paginated and sorted by creation date (newest first).
    """
    # Query total count
    count_stmt = select(func.count()).select_from(Claim)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar_one()

    # Query claims and outer join to fetch Member name
    stmt = (
        select(Claim, Member.name)
        .outerjoin(Member, Claim.member_id == Member.member_id)
        .order_by(Claim.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    rows = res.all()

    claims_list = []
    for claim, member_name in rows:
        claims_list.append(prepare_claim_response(claim, member_name or "Unknown Member"))

    import math
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = math.ceil(total / limit) if limit > 0 else 1

    return ClaimsListResponse(
        claims=claims_list,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Returns aggregated stats for all claims.
    """
    stmt = select(Claim)
    res = await db.execute(stmt)
    claims = res.scalars().all()
    
    total = len(claims)
    approved = sum(1 for c in claims if c.decision == "APPROVED")
    rejected = sum(1 for c in claims if c.decision == "REJECTED")
    partial = sum(1 for c in claims if c.decision == "PARTIAL")
    manual_review = sum(1 for c in claims if c.decision == "MANUAL_REVIEW")
    
    total_approved = sum(float(c.approved_amount) if c.approved_amount is not None else 0.0 for c in claims)
    
    confidences = [float(c.confidence_score) for c in claims if c.confidence_score is not None]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    return StatsResponse(
        total=total,
        approved=approved,
        rejected=rejected,
        partial=partial,
        manual_review=manual_review,
        total_approved_amount=total_approved,
        avg_confidence=avg_confidence
    )

@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves a single claim by its claim_id.
    """
    stmt = (
        select(Claim, Member.name)
        .outerjoin(Member, Claim.member_id == Member.member_id)
        .where(Claim.claim_id == claim_id)
    )
    res = await db.execute(stmt)
    row = res.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Claim not found")

    claim, member_name = row
    return prepare_claim_response(claim, member_name or "Unknown Member")

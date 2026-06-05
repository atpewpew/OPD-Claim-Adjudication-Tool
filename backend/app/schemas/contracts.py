from pydantic import BaseModel, Field
from datetime import date, datetime

class ClaimSubmitForm(BaseModel):
    member_id: str
    treatment_date: date
    claim_amount: float = Field(gt=0)
    hospital_name: str | None = None
    cashless_request: bool = False
    pre_auth_provided: bool = False
    previous_claims_same_day: int = Field(default=0, ge=0)

# Alias for compatibility with other documentation
ClaimSubmitRequest = ClaimSubmitForm

class AdjudicationResult(BaseModel):
    decision: str  # APPROVED | REJECTED | PARTIAL | MANUAL_REVIEW
    approved_amount: float = 0.0
    rejection_reasons: list[str] = Field(default_factory=list)
    rejected_items: list[str] = Field(default_factory=list)
    rule_matrix: dict = Field(default_factory=dict)
    deductions: dict = Field(default_factory=dict)
    confidence_score: float = 1.0
    notes: str = ""
    next_steps: str = ""

class ClaimResponse(BaseModel):
    claim_id: str
    member_id: str
    member_name: str
    treatment_date: date
    submitted_amount: float
    hospital_name: str | None = None
    decision: str
    approved_amount: float | None = None
    rejection_reasons: list[str] = Field(default_factory=list)
    rejected_items: list[str] = Field(default_factory=list)
    rule_matrix: dict = Field(default_factory=dict)
    deductions: dict = Field(default_factory=dict)
    confidence_score: float | None = None
    notes: str | None = None
    next_steps: str | None = None
    extracted_data: dict | None = None
    document_urls: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}

class ClaimsListResponse(BaseModel):
    claims: list[ClaimResponse]
    total: int
    page: int
    limit: int
    pages: int

class StatsResponse(BaseModel):
    total: int
    approved: int
    rejected: int
    partial: int
    manual_review: int
    total_approved_amount: float
    avg_confidence: float

class AppealRequest(BaseModel):
    note: str = Field(min_length=10)

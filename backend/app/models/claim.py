from sqlalchemy import Column, String, Date, Numeric, Boolean, Integer, Text, DateTime, JSON
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String(50), unique=True, nullable=False, index=True)
    member_id = Column(String(20), nullable=False, index=True)   # soft FK to members.member_id
    treatment_date = Column(Date, nullable=False)
    submitted_amount = Column(Numeric(10, 2), nullable=False)
    hospital_name = Column(String(255), nullable=True)
    cashless_request = Column(Boolean, default=False)
    pre_auth_provided = Column(Boolean, default=False)
    previous_claims_same_day = Column(Integer, default=0)

    document_urls = Column(JSON, nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)
    ai_extraction_raw = Column(JSON, nullable=True)

    decision = Column(String(20), default="PENDING")
    approved_amount = Column(Numeric(10, 2), nullable=True)
    rejection_reasons = Column(JSON, nullable=True)
    rule_matrix = Column(JSON, nullable=True)
    deductions = Column(JSON, nullable=True)
    confidence_score = Column(Numeric(4, 2), nullable=True)
    notes = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    appeal_note = Column(Text, nullable=True)
    appealed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Claim {self.claim_id} - {self.decision}>"

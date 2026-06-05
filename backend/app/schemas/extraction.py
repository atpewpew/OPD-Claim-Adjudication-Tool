from pydantic import BaseModel, Field

class ExtractionResult(BaseModel):
    # Doctor information
    doctor_name: str | None = None
    doctor_registration: str | None = None  # e.g. "KA/45678/2015" or "AYUR/KL/2345/2019"

    # Patient information
    patient_name: str | None = None
    patient_age: int | None = None

    # Medical details
    diagnosis: str | None = None
    medicines: list[str] = Field(default_factory=list)
    procedures: list[str] = Field(default_factory=list)
    treatment_type: str = "allopathic"  # "allopathic" | "ayurvedic" | "homeopathic"

    # Financial details — all floats, no currency symbols
    consultation_fee: float | None = None
    medicine_cost: float | None = None
    diagnostic_cost: float | None = None
    total_amount: float | None = None

    # Document metadata
    treatment_date: str | None = None  # YYYY-MM-DD
    document_types_found: list[str] = Field(default_factory=list)  # ["prescription", "bill", "report"]
    has_prescription: bool = False

    # Quality indicators
    extraction_confidence: float = 0.0  # 0.0 to 1.0
    anomaly_flags: list[str] = Field(default_factory=list)

from sqlalchemy import Column, String, Date, Integer, Numeric, DateTime
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

class Member(Base):
    __tablename__ = "members"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    join_date = Column(Date, nullable=False)
    annual_limit = Column(Integer, default=50000)
    annual_claims_used = Column(Numeric(10, 2), default=0.0)
    policy_id = Column(String(50), default="PLUM_OPD_2024")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Member {self.member_id} - {self.name}>"

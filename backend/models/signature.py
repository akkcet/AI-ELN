from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from ..database import Base

class ExperimentSignature(Base):
    __tablename__ = "experiment_signatures"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, index=True)
    signed_by = Column(String)
    action = Column(String)          # SUBMIT / APPROVE
    reason = Column(String, nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow)
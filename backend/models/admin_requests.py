from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from ..database import Base

class AdminRequest(Base):
    __tablename__ = "admin_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    request_type = Column(String, nullable=False)
    payload = Column(Text, nullable=False)              # JSON string
    status = Column(String, default="NewRequest")

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    executed_by = Column(String, nullable=True)
    executed_at = Column(DateTime, nullable=True)
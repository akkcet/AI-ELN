from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.database import Base 

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String)
    action = Column(String)
    entity = Column(String)
    entity_id = Column(String)
    details = Column(String)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

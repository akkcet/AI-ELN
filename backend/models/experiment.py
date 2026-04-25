from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from ..database import Base
from sqlalchemy import Text

class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    project_id = Column(Integer)
    category_id = Column(Integer)
    status = Column(String, default="New")
    sections = Column(Text)  # JSON list of sections
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

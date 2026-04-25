from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from ..database import Base

class ExperimentVersion(Base):
    __tablename__ = "experiment_versions"

    version_id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String, ForeignKey("experiments.experiment_id"))
    version = Column(Integer)
    data_json = Column(Text)
    hash_value = Column(String)
    saved_by = Column(String)
    saved_at = Column(DateTime, default=datetime.utcnow)

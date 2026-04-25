# backend/models/masterdata.py# backend/models 
from sqlalchemy import Column, String, Integer, DateTime,Text,ForeignKey
#from datetime import datetime
from sqlalchemy.orm import relationship
from ..database import Base
from fastapi import  Depends, HTTPException



# --------------------------------------
# ✅ Project Table
# --------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)


# --------------------------------------
# ✅ Lookup Table
# --------------------------------------
class Lookup(Base):
    __tablename__ = "lookups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    # Relationship with lookup values
    values = relationship("LookupValue", back_populates="lookup", cascade="all,delete")


# --------------------------------------
# ✅ Lookup Values Table
# --------------------------------------
class LookupValue(Base):
    __tablename__ = "lookup_values"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lookup_id = Column(Integer, ForeignKey("lookups.id"), nullable=False)
    value = Column(String, nullable=False)

    lookup = relationship("Lookup", back_populates="values")


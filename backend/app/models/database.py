from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CostSnapshot(Base):
    __tablename__ = "cost_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    service = Column(String, nullable=False, index=True)
    cost = Column(Float, nullable=False)
    unit = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)

class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    service = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    threshold_percentage = Column(Float, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TagCompliance(Base):
    __tablename__ = "tag_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String, nullable=False, index=True)
    resource_name = Column(String)
    resource_type = Column(String, nullable=False)
    service = Column(String, nullable=False)
    missing_tags = Column(Text)
    scan_date = Column(DateTime, default=datetime.utcnow)

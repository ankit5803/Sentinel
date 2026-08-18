# backend/app/models/models.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from app.db.database import Base

class PredictionLog(Base):
    """
    SQLAlchemy model representing the 'prediction_logs' table in PostgreSQL.
    Every time Sentinel analyzes a message, it gets saved here for audit and drift detection.
    """
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Input data
    text = Column(Text, nullable=False)
    language_detected = Column(String(50), nullable=False)
    
    # Risk Engine Outputs
    threat_probability = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False, index=True)
    immediacy = Column(String(50), nullable=False)
    target_identified = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

if __name__ == "__main__":
    print(f"✅ Models loaded. Table name is: {PredictionLog.__tablename__}")
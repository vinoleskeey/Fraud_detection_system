from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, JSON
from utils.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    features = Column(JSON, nullable=False)
    time = Column(Float)
    amount = Column(Float)
    is_fraud = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TransactionCreate(BaseModel):
    Time: Optional[float] = Field(None)
    V1: float = Field(...)
    V2: float = Field(...)
    V3: float = Field(...)
    V4: float = Field(...)
    V5: float = Field(...)
    V6: float = Field(...)
    V7: float = Field(...)
    V8: float = Field(...)
    V9: float = Field(...)
    V10: float = Field(...)
    V11: float = Field(...)
    V12: float = Field(...)
    V13: float = Field(...)
    V14: float = Field(...)
    V15: float = Field(...)
    V16: float = Field(...)
    V17: float = Field(...)
    V18: float = Field(...)
    V19: float = Field(...)
    V20: float = Field(...)
    V21: float = Field(...)
    V22: float = Field(...)
    V23: float = Field(...)
    V24: float = Field(...)
    V25: float = Field(...)
    V26: float = Field(...)
    V27: float = Field(...)
    V28: float = Field(...)
    Amount: float = Field(..., ge=0)

class TransactionResponse(BaseModel):
    id: int
    features: Dict
    time: Optional[float]
    amount: Optional[float]
    is_fraud: bool
    confidence: float
    risk_score: float
    created_at: datetime

    model_config = {"from_attributes": True}

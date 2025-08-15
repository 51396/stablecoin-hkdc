from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from .base import Base

class TotalSupplyHistory(Base):
    __tablename__ = 'total_supply_history'
    id = Column(Integer, primary_key=True, index=True)
    total_supply = Column(Float, nullable=False)
    decimals = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
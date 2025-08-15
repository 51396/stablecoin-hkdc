from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from .base import Base

class Whitelist(Base):
    __tablename__ = 'whitelist'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    added_at = Column(DateTime, default=datetime.utcnow)
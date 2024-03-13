from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .engine import Base

class ParseError(Base):
    __tablename__ = 'parse_errors'

    id = Column(Integer, primary_key=True, index=True)
    link = Column(String(256), nullable=False)
    error = Column(Text())
    count = Column(Integer())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

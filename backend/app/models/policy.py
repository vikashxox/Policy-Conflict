from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database.session import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(120), nullable=False)
    owner = Column(String(120), nullable=False)
    department = Column(String(120), nullable=False)
    version = Column(String(80), nullable=False)
    effective_date = Column(String(80), nullable=True)
    last_reviewed = Column(String(80), nullable=True)
    health = Column(Integer, default=100)
    severity = Column(String(40), default="healthy")
    status = Column(String(40), default="active")
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

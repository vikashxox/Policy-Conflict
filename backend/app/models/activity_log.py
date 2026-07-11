from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database.session import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(120), nullable=False)
    action = Column(String(120), nullable=False)
    target = Column(String(255), nullable=False)
    severity = Column(String(40), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

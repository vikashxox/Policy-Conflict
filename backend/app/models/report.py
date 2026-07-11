from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_format = Column(String(40), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

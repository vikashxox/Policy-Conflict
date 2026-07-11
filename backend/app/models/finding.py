from sqlalchemy import Column, Integer, String, Text

from backend.app.database.session import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    severity = Column(String(40), nullable=False)
    finding_type = Column(String(80), nullable=False)
    policy_a = Column(String(255), nullable=False)
    policy_b = Column(String(255), nullable=False)
    section = Column(String(120), nullable=False)
    confidence = Column(Integer, default=0)
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    compliance = Column(String(255), nullable=False)
    status = Column(String(40), default="open")
    category = Column(String(120), nullable=False)

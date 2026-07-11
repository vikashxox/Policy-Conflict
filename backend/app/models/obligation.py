from sqlalchemy import Column, Integer, String, Text

from backend.app.database.session import Base


class Obligation(Base):
    __tablename__ = "obligations"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    strength = Column(String(40), nullable=False)
    scope = Column(String(80), nullable=False)
    category = Column(String(80), nullable=False)
    action = Column(Text, nullable=False)

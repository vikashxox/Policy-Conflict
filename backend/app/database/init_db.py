from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.activity_log import ActivityLog
from backend.app.models.finding import Finding
from backend.app.models.obligation import Obligation
from backend.app.models.policy import Policy
from backend.app.models.report import Report
from backend.app.models.user import User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_default_admin_user()


def seed_default_admin_user() -> None:
    session = SessionLocal()
    try:
        username = getattr(settings, "default_admin_username", "admin")
        password = getattr(settings, "default_admin_password", "admin123")
        existing = session.query(User).filter(User.username == username).first()
        if existing is None:
            session.add(
                User(
                    username=username,
                    email=f"{username}@policy-guardian.local",
                    hashed_password=get_password_hash(password),
                    is_active=True,
                )
            )
            session.commit()
    finally:
        session.close()

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
    seed_dataset()


def seed_dataset() -> None:
    from backend.app.services.dataset_loader import DatasetLoaderService
    session = SessionLocal()
    try:
        loader = DatasetLoaderService()
        loader.seed_database(session)
    finally:
        session.close()


def seed_default_admin_user() -> None:
    """Seed the default admin account: admin@gmail.com / admin123."""
    session = SessionLocal()
    try:
        existing = session.query(User).filter(
            (User.username == "admin") | (User.email == "admin@gmail.com")
        ).first()
        if existing is None:
            session.add(
                User(
                    username="admin",
                    email="admin@gmail.com",
                    hashed_password=get_password_hash("admin123"),
                    is_active=True,
                )
            )
            session.commit()
        else:
            # Ensure credentials are up to date
            existing.username = "admin"
            existing.email = "admin@gmail.com"
            existing.hashed_password = get_password_hash("admin123")
            existing.is_active = True
            session.commit()
    finally:
        session.close()

from sqlalchemy.orm import Session

from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.policy_repository_db import PolicyRepositoryDB
from backend.app.database.session import SessionLocal


class PersistenceService:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session or SessionLocal()
        self.user_repository = UserRepository(self.session)
        self.policy_repository = PolicyRepositoryDB(self.session)

    def get_user_repository(self) -> UserRepository:
        return self.user_repository

    def get_policy_repository(self) -> PolicyRepositoryDB:
        return self.policy_repository

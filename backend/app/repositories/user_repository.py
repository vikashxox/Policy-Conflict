from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.core.security import get_password_hash


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, identifier: str) -> User | None:
        return (
            self.session.query(User)
            .filter((User.username == identifier) | (User.email == identifier))
            .first()
        )

    def create(self, username: str, email: str, password: str) -> User:
        user = User(username=username, email=email, hashed_password=get_password_hash(password))
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any

import jwt

from backend.app.core.config import settings


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()

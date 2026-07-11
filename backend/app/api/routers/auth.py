from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from backend.app.core.config import settings
from backend.app.core.security import create_access_token, verify_password
from backend.app.database.session import SessionLocal
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class AuthService:
    def authenticate(self, username: str, password: str) -> tuple[dict, str]:
        session = SessionLocal()
        repository = UserRepository(session)
        user = repository.get_by_username(username)
        if user and verify_password(password, user.hashed_password):
            payload = {"id": user.id, "username": user.username, "email": user.email}
            session.close()
            return payload, create_access_token(username)
        session.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


service = AuthService()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user, token = service.authenticate(payload.username, payload.password)
    return TokenResponse(access_token=token, user=UserOut(**user))


@router.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return {"user": {"username": payload.get("sub")}}

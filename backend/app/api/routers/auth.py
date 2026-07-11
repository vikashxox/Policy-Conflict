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
    def authenticate(self, identifier: str, password: str) -> tuple[dict, str]:
        session = SessionLocal()
        repository = UserRepository(session)
        user = repository.get_by_username_or_email(identifier)
        if user and verify_password(password, user.hashed_password):
            display_name = user.username or (user.email or "Policy User")
            payload = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": display_name,
                "role": "admin",
            }
            session.close()
            return payload, create_access_token(user.username)
        session.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


service = AuthService()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    identifier = payload.email or payload.username or ""
    user, token = service.authenticate(identifier, payload.password)
    return TokenResponse(access_token=token, user=UserOut(**user))


@router.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    return {
        "user": {
            "id": payload.get("id"),
            "username": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name") or payload.get("sub"),
            "role": payload.get("role") or "admin",
        }
    }

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from backend.app.core.config import settings
from backend.app.core.security import create_access_token, verify_password
from backend.app.database.session import SessionLocal
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

security_scheme = HTTPBearer(auto_error=False)


def security(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> HTTPAuthorizationCredentials:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials


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
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    session = SessionLocal()
    try:
        repository = UserRepository(session)
        user = repository.get_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "name": user.username,
                "role": "admin",
            }
        }
    finally:
        session.close()

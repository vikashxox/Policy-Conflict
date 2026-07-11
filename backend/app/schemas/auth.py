from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    username: str | None = Field(default=None, min_length=1)
    email: str | None = Field(default=None, min_length=1)
    password: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_identity(self) -> "LoginRequest":
        if not self.username and not self.email:
            raise ValueError("Either username or email is required")
        return self


class UserOut(BaseModel):
    id: int
    username: str
    email: str | None = None
    name: str | None = None
    role: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

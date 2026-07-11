from pydantic import BaseModel, Field


class ParsedPolicy(BaseModel):
    policy_name: str
    version: str
    department: str
    owner: str
    effective_date: str | None = None
    last_reviewed: str | None = None
    sections: int = Field(default=0)
    raw_text: str


class UploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    parsed: ParsedPolicy

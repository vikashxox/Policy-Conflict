from pydantic import BaseModel, Field


class PolicyBase(BaseModel):
    name: str
    category: str
    owner: str
    department: str
    version: str
    effective_date: str
    last_reviewed: str
    health: int = Field(ge=0, le=100)
    severity: str
    status: str
    summary: str


class PolicyOut(PolicyBase):
    id: str


class FindingOut(BaseModel):
    id: str
    severity: str
    type: str
    policy_a: str
    policy_b: str
    section: str
    confidence: int
    description: str
    recommendation: str
    compliance: str
    status: str
    category: str


class DashboardResponse(BaseModel):
    kpis: dict
    findings: list[FindingOut]
    policies: list[PolicyOut]
    recent_uploads: list[dict]
    activity: list[dict]

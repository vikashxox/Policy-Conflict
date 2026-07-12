from pydantic import BaseModel, Field


class PolicyOut(BaseModel):
    id: str
    name: str
    category: str
    owner: str
    department: str
    version: str
    effectiveDate: str
    lastReviewed: str
    health: int = Field(ge=0, le=100)
    severity: str
    status: str
    summary: str


class FindingOut(BaseModel):
    id: str
    severity: str
    type: str
    policyA: str
    policyB: str
    section: str
    confidence: int
    description: str
    recommendation: str
    compliance: str
    status: str
    category: str


class PolicyListResponse(BaseModel):
    items: list[PolicyOut]


class PolicyDetailResponse(BaseModel):
    policy: PolicyOut
    obligations: list[str]
    relatedFindings: list[FindingOut]


class FindingListResponse(BaseModel):
    items: list[FindingOut]


class DashboardResponse(BaseModel):
    organization: dict
    kpis: dict
    kpiMetrics: list[dict]
    healthBreakdown: list[dict]
    policiesByCategory: list[dict]
    healthTrend: list[dict]
    conflictTrend: list[dict]
    complianceDistribution: list[dict]
    complianceFrameworks: list[dict]
    aiInsights: list[dict]
    aiRecommendation: str
    findings: list[FindingOut]
    recentUploads: list[dict]
    activity: list[dict]
    graphNodes: list[dict]
    graphLinks: list[dict]

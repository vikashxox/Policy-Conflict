from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from backend.app.api.routers.auth import security
from backend.app.services.policy_service import PolicyService
from backend.app.services.upload_service import UploadService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.policy_health_service import PolicyHealthService
from backend.app.services.ai_insights_service import AiInsightsService
from backend.app.services.persistence_service import PersistenceService
from backend.app.report.report_service import ReportService
from backend.app.schemas.policy import DashboardResponse, FindingOut, PolicyOut

router = APIRouter(prefix="/api", tags=["policy"])
service = PolicyService()
upload_service = UploadService()
analysis_service = AnalysisService()
health_service = PolicyHealthService()
ai_service = AiInsightsService()
report_service = ReportService()
persistence_service = PersistenceService()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(_: object = Depends(security)) -> DashboardResponse:
    return service.get_dashboard()


@router.get("/policies", response_model=list[PolicyOut])
def policies(_: object = Depends(security)) -> list[PolicyOut]:
    repository = persistence_service.get_policy_repository()
    policies = repository.list_policies()
    return [PolicyOut(id=str(policy.external_id), name=policy.name, category=policy.category, owner=policy.owner, department=policy.department, version=policy.version, effective_date=policy.effective_date or "", last_reviewed=policy.last_reviewed or "", health=policy.health, severity=policy.severity, status=policy.status, summary=policy.summary or "") for policy in policies]


@router.get("/policies/{policy_id}", response_model=PolicyOut)
def policy_detail(policy_id: str, _: object = Depends(security)) -> PolicyOut:
    policy = service.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return policy


@router.get("/findings", response_model=list[FindingOut])
def findings(_: object = Depends(security)) -> list[FindingOut]:
    return service.list_findings()


@router.get("/reports")
def reports(_: object = Depends(security)) -> dict:
    return {
        "reports": [
            {
                "id": "R-001",
                "title": "Executive Audit Summary",
                "desc": "Highlights critical conflicts and stale policy exposure.",
                "format": "PDF",
                "updated": "2h ago",
                "pages": 12,
                "download_url": "/reports/executive-audit-summary.pdf",
            },
            {
                "id": "R-002",
                "title": "Findings Export",
                "desc": "Machine-readable findings snapshot for SOC teams.",
                "format": "JSON",
                "updated": "1d ago",
                "pages": 0,
                "download_url": "/reports/findings-export.json",
            },
            {
                "id": "R-003",
                "title": "Compliance Workbook",
                "desc": "Excel workbook with policy and findings coverage.",
                "format": "Excel",
                "updated": "3d ago",
                "pages": 0,
                "download_url": "/reports/compliance-workbook.xlsx",
            },
        ]
    }


@router.post("/analyze")
def analyze(_: object = Depends(security)) -> dict:
    sample_a = "The policy shall require MFA for all users. Users must rotate passwords every 30 days."
    sample_b = "The standard requires no periodic password rotation. Users must not be forced to rotate passwords."
    insights = ai_service.generate_insights(
        conflicts=[{"severity": "critical"}],
        stale_policies=[{"reason": "Policy older than 18 months"}],
        duplicates=[{"is_duplicate": True}],
    )
    return {
        "status": "completed",
        "summary": "Policies analyzed successfully",
        "health_score": insights["health_score"],
        "critical_findings": insights["critical_findings"],
        "recommendations": insights["recommendations"],
        "risk_level": insights["risk_level"],
        "analysis": analysis_service.analyze_texts(sample_a, sample_b),
        "health": health_service.evaluate(sample_a, "2022-01-01"),
        "reports": [
            report_service.generate_report("Executive Summary", {"insights": insights}, report_format="pdf"),
            report_service.generate_report("Findings Export", {"insights": insights}, report_format="json"),
            report_service.generate_report("Compliance Workbook", {"insights": insights}, report_format="excel"),
        ],
    }


@router.post("/upload")
def upload(file: UploadFile, _: object = Depends(security)) -> dict:
    content = file.file.read()
    return upload_service.process_upload(file.filename or "policy.txt", content)


@router.delete("/policies/{policy_id}")
def delete_policy(policy_id: str, _: object = Depends(security)) -> dict:
    return {"status": "deleted", "policy_id": policy_id}

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.routers.auth import security
from backend.app.database.session import SessionLocal
from backend.app.repositories.policy_repository_db import PolicyRepositoryDB
from backend.app.schemas.policy import (
    DashboardResponse,
    PolicyListResponse,
    PolicyDetailResponse,
    FindingListResponse,
)
from backend.app.services.upload_service import UploadService
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.policy_health_service import PolicyHealthService
from backend.app.services.ai_insights_service import AiInsightsService
from backend.app.report.report_service import ReportService

router = APIRouter(prefix="/api", tags=["policy"])

upload_service = UploadService()
analysis_service = AnalysisService()
health_service = PolicyHealthService()
ai_service = AiInsightsService()
report_service = ReportService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    repository = PolicyRepositoryDB(db)

    # ── KPIs (all from DB) ────────────────────────────────────────────
    kpis = repository.get_dashboard_kpis()

    # ── KPI metric cards ─────────────────────────────────────────────
    kpi_metrics = [
        {
            "label":  "Total Policies",
            "value":  kpis["totalPolicies"],
            "icon":   "FileText",
            "tint":   "text-primary bg-primary/15",
            "trend":  "up",
            "change": f"+{kpis['totalPolicies']}",
            "good":   "up",
            "spark":  [kpis["totalPolicies"]] * 8,
        },
        {
            "label":  "Healthy Policies",
            "value":  kpis["healthyPolicies"],
            "icon":   "ShieldCheck",
            "tint":   "text-success bg-success/15",
            "trend":  "up" if kpis["healthyPolicies"] > 0 else "down",
            "change": str(kpis["healthyPolicies"]),
            "good":   "up",
            "spark":  [kpis["healthyPolicies"]] * 8,
        },
        {
            "label":  "Conflicts",
            "value":  kpis["conflicts"],
            "icon":   "GitCompareArrows",
            "tint":   "text-critical bg-critical/15",
            "trend":  "down" if kpis["conflicts"] < 10 else "up",
            "change": str(kpis["conflicts"]),
            "good":   "down",
            "spark":  [kpis["conflicts"]] * 8,
        },
        {
            "label":  "Duplicates",
            "value":  kpis["duplicates"],
            "icon":   "Copy",
            "tint":   "text-warning bg-warning/15",
            "trend":  "down" if kpis["duplicates"] == 0 else "up",
            "change": str(kpis["duplicates"]),
            "good":   "down",
            "spark":  [kpis["duplicates"]] * 8,
        },
        {
            "label":  "Stale Policies",
            "value":  kpis["stale"],
            "icon":   "Clock",
            "tint":   "text-warning bg-warning/15",
            "trend":  "down" if kpis["stale"] < 5 else "up",
            "change": str(kpis["stale"]),
            "good":   "down",
            "spark":  [kpis["stale"]] * 8,
        },
        {
            "label":  "Health Score",
            "value":  kpis["healthScore"],
            "suffix": "%",
            "icon":   "HeartPulse",
            "tint":   "text-success bg-success/15",
            "trend":  "up" if kpis["healthScore"] >= 65 else "down",
            "change": f"{kpis['healthScore']}%",
            "good":   "up",
            "spark":  [kpis["healthScore"]] * 8,
        },
    ]

    # ── Charts (all real DB data) ─────────────────────────────────────
    health_breakdown       = repository.get_health_breakdown()
    compliance_distribution = repository.get_compliance_distribution()
    policies_by_category   = repository.get_policies_by_category()
    health_trend           = repository.get_health_trend(months=6)
    conflict_trend         = repository.get_conflict_trend(months=6)

    # ── Compliance frameworks from AI insights ────────────────────────
    full_insights = ai_service.analyze_from_db(db)
    compliance_frameworks = full_insights.get("compliance_summary", [])

    # ── Recent uploads from ActivityLog ──────────────────────────────
    recent_uploads = repository.get_recent_uploads(limit=5)

    # ── Graph data ────────────────────────────────────────────────────
    graph_nodes, graph_links = repository.get_graph_data()

    # ── Findings preview (top 10, not truncated to 5) ─────────────────
    findings = [
        {
            "id":             f"F-{f.id}",
            "severity":       f.severity,
            "type":           f.finding_type,
            "policyA":        f.policy_a,
            "policyB":        f.policy_b,
            "section":        f.section,
            "confidence":     f.confidence,
            "description":    f.description,
            "recommendation": f.recommendation,
            "compliance":     f.compliance,
            "status":         f.status,
            "category":       f.category,
        }
        for f in repository.list_findings()[:10]
    ]

    # ── Activity log ─────────────────────────────────────────────────
    activities = [
        {
            "id":       f"A-{act.id}",
            "actor":    act.actor,
            "action":   act.action,
            "target":   act.target,
            "time":     act.created_at.strftime("%b %d, %I:%M %p") if act.created_at else "—",
            "severity": act.severity,
        }
        for act in repository.list_activities(limit=15)
    ]

    # ── AI Insights ───────────────────────────────────────────────────
    ai_insights_raw = full_insights.get("critical_issues", [])
    if not ai_insights_raw:
        ai_insights_raw = [
            {
                "id":       "AI-OK",
                "severity": "healthy",
                "text":     "All policies are fully compliant and healthy.",
                "icon":     "ShieldCheck",
            }
        ]

    ai_recommendation = (
        full_insights["recommendations"][0]
        if full_insights.get("recommendations")
        else "Maintain current policy governance."
    )

    last_analysis = repository.get_last_activity_time()

    return {
        "organization": {
            "name":         "GRC Hackathon Corp",
            "admin":        "admin",
            "lastAnalysis": last_analysis,
            "lastUpload":   recent_uploads[0]["name"] if recent_uploads else "—",
        },
        "kpis":                   kpis,
        "kpiMetrics":             kpi_metrics,
        "healthBreakdown":        health_breakdown,
        "policiesByCategory":     policies_by_category,
        "healthTrend":            health_trend,
        "conflictTrend":          conflict_trend,
        "complianceDistribution": compliance_distribution,
        "complianceFrameworks":   compliance_frameworks,
        "aiInsights":             ai_insights_raw,
        "aiRecommendation":       ai_recommendation,
        "topRisks":               full_insights.get("top_risks", []),
        "orgRisk": {
            "score":   full_insights["org_risk_score"],
            "status":  full_insights["org_risk_status"],
            "summary": full_insights["org_risk_summary"],
        },
        "findings":      findings,
        "recentUploads": recent_uploads,
        "activity":      activities,
        "graphNodes":    graph_nodes,
        "graphLinks":    graph_links,
    }



@router.get("/policies", response_model=PolicyListResponse)
def policies(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    repository = PolicyRepositoryDB(db)
    items = []
    for policy in repository.list_policies():
        items.append(
            {
                "id": policy.external_id,
                "name": policy.name,
                "category": policy.category,
                "owner": policy.owner,
                "department": policy.department,
                "version": policy.version,
                "effectiveDate": policy.effective_date or "",
                "lastReviewed": policy.last_reviewed or "",
                "health": policy.health,
                "severity": policy.severity,
                "status": policy.status,
                "summary": policy.summary or "",
            }
        )
    return {"items": items}


@router.get("/policies/{policy_id}", response_model=PolicyDetailResponse)
def policy_detail(
    policy_id: str, db: Session = Depends(get_db), _: object = Depends(security)
) -> dict:
    repository = PolicyRepositoryDB(db)
    policy = repository.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    policy_out = {
        "id": policy.external_id,
        "name": policy.name,
        "category": policy.category,
        "owner": policy.owner,
        "department": policy.department,
        "version": policy.version,
        "effectiveDate": policy.effective_date or "",
        "lastReviewed": policy.last_reviewed or "",
        "health": policy.health,
        "severity": policy.severity,
        "status": policy.status,
        "summary": policy.summary or "",
    }

    obligations = [ob.text for ob in repository.get_obligations_for_policy(policy.id)]

    related_findings = [
        {
            "id": f"F-{f.id}",
            "severity": f.severity,
            "type": f.finding_type,
            "policyA": f.policy_a,
            "policyB": f.policy_b,
            "section": f.section,
            "confidence": f.confidence,
            "description": f.description,
            "recommendation": f.recommendation,
            "compliance": f.compliance,
            "status": f.status,
            "category": f.category,
        }
        for f in repository.get_findings_for_policy(policy.name)
    ]

    return {
        "policy": policy_out,
        "obligations": obligations,
        "relatedFindings": related_findings,
    }


@router.get("/findings", response_model=FindingListResponse)
def findings(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    repository = PolicyRepositoryDB(db)
    items = []
    for f in repository.list_findings():
        items.append(
            {
                "id": f"F-{f.id}",
                "severity": f.severity,
                "type": f.finding_type,
                "policyA": f.policy_a,
                "policyB": f.policy_b,
                "section": f.section,
                "confidence": f.confidence,
                "description": f.description,
                "recommendation": f.recommendation,
                "compliance": f.compliance,
                "status": f.status,
                "category": f.category,
            }
        )
    return {"items": items}


@router.get("/reports")
def reports(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    """Generate and return reports list derived from live DB findings and policies."""
    from backend.app.repositories.policy_repository_db import PolicyRepositoryDB
    from backend.app.services.ai_insights_service import AiInsightsService

    repository = PolicyRepositoryDB(db)
    all_findings = repository.list_findings()
    all_policies = repository.list_policies()
    insights     = AiInsightsService().analyze_from_db(db)

    now_label = __import__("datetime").datetime.now().strftime("%b %d, %Y")
    
    # 4 Report Types: Executive, Technical, Audit, Compliance
    # 3 Formats: PDF, Excel, JSON
    reports_list = []
    
    # Executive
    reports_list.append({
        "id": "R-1",
        "title": "Executive Report",
        "desc": f"High-level policy health overview and risk posture (Score: {insights['health_score']}%).",
        "format": "PDF",
        "updated": now_label,
        "pages": 2,
        "downloadUrl": "/api/reports/download/executive-report.pdf",
        "download_url": "/api/reports/download/executive-report.pdf"
    })
    reports_list.append({
        "id": "R-2",
        "title": "Executive Report",
        "desc": "High-level summary KPIs and recommendations table.",
        "format": "Excel",
        "updated": now_label,
        "pages": 1,
        "downloadUrl": "/api/reports/download/executive-report.xlsx",
        "download_url": "/api/reports/download/executive-report.xlsx"
    })
    reports_list.append({
        "id": "R-3",
        "title": "Executive Report",
        "desc": "Machine-readable GRC overview summary data.",
        "format": "JSON",
        "updated": now_label,
        "pages": 0,
        "downloadUrl": "/api/reports/download/executive-report.json",
        "download_url": "/api/reports/download/executive-report.json"
    })

    # Technical
    reports_list.append({
        "id": "R-4",
        "title": "Technical Report",
        "desc": f"Detailed listing of all {insights['critical_findings']} conflicts and engineering findings.",
        "format": "PDF",
        "updated": now_label,
        "pages": 3,
        "downloadUrl": "/api/reports/download/technical-report.pdf",
        "download_url": "/api/reports/download/technical-report.pdf"
    })
    reports_list.append({
        "id": "R-5",
        "title": "Technical Report",
        "desc": "Engineering findings worksheet with full conflict metadata.",
        "format": "Excel",
        "updated": now_label,
        "pages": 2,
        "downloadUrl": "/api/reports/download/technical-report.xlsx",
        "download_url": "/api/reports/download/technical-report.xlsx"
    })
    reports_list.append({
        "id": "R-6",
        "title": "Technical Report",
        "desc": "Comprehensive findings JSON dump for security pipelines.",
        "format": "JSON",
        "updated": now_label,
        "pages": 0,
        "downloadUrl": "/api/reports/download/technical-report.json",
        "download_url": "/api/reports/download/technical-report.json"
    })

    # Audit
    reports_list.append({
        "id": "R-7",
        "title": "Audit Report",
        "desc": f"Official GRC policy compliance & audit trail report across {insights['total_policies']} policies.",
        "format": "PDF",
        "updated": now_label,
        "pages": 4,
        "downloadUrl": "/api/reports/download/audit-report.pdf",
        "download_url": "/api/reports/download/audit-report.pdf"
    })
    reports_list.append({
        "id": "R-8",
        "title": "Audit Report",
        "desc": "Comprehensive policies and audit findings status workbook.",
        "format": "Excel",
        "updated": now_label,
        "pages": 3,
        "downloadUrl": "/api/reports/download/audit-report.xlsx",
        "download_url": "/api/reports/download/audit-report.xlsx"
    })
    reports_list.append({
        "id": "R-9",
        "title": "Audit Report",
        "desc": "Audit-trail log data formatted in standard JSON.",
        "format": "JSON",
        "updated": now_label,
        "pages": 0,
        "downloadUrl": "/api/reports/download/audit-report.json",
        "download_url": "/api/reports/download/audit-report.json"
    })

    # Compliance
    reports_list.append({
        "id": "R-10",
        "title": "Compliance Report",
        "desc": "Security framework mapping (GDPR, ISO, NIST, etc.) status report.",
        "format": "PDF",
        "updated": now_label,
        "pages": 2,
        "downloadUrl": "/api/reports/download/compliance-report.pdf",
        "download_url": "/api/reports/download/compliance-report.pdf"
    })
    reports_list.append({
        "id": "R-11",
        "title": "Compliance Report",
        "desc": "Compliance matrix sheet aligning policies to controls.",
        "format": "Excel",
        "updated": now_label,
        "pages": 2,
        "downloadUrl": "/api/reports/download/compliance-report.xlsx",
        "download_url": "/api/reports/download/compliance-report.xlsx"
    })
    reports_list.append({
        "id": "R-12",
        "title": "Compliance Report",
        "desc": "Structured GRC compliance mappings in machine-readable format.",
        "format": "JSON",
        "updated": now_label,
        "pages": 0,
        "downloadUrl": "/api/reports/download/compliance-report.json",
        "download_url": "/api/reports/download/compliance-report.json"
    })

    return {"items": reports_list}


@router.get("/reports/download/{filename}")
def download_report(
    filename: str,
    db: Session = Depends(get_db),
    _: object = Depends(security)
):
    """Generate and stream the requested report file (PDF, Excel, JSON)."""
    import re
    from fastapi.responses import StreamingResponse
    import io
    from fastapi import HTTPException

    match = re.match(r"^([a-zA-Z0-9_-]+)-report\.(pdf|xlsx|json)$", filename.lower())
    if not match:
        raise HTTPException(status_code=400, detail="Invalid filename format. Expected: {type}-report.{ext}")

    report_type, ext = match.groups()
    report_format = "excel" if ext == "xlsx" else ext

    # Fetch data from DB
    from backend.app.repositories.policy_repository_db import PolicyRepositoryDB
    from backend.app.services.ai_insights_service import AiInsightsService

    repository = PolicyRepositoryDB(db)
    all_findings = repository.list_findings()
    all_policies = repository.list_policies()
    insights = AiInsightsService().analyze_from_db(db)

    # Extra summary info for report
    insights["healthy_policies"] = sum(1 for p in all_policies if p.severity == "healthy")

    # Generate Report
    from backend.app.report.report_service import ReportService
    rs = ReportService()
    try:
        file_bytes, content_type, out_filename = rs.generate_report_file(
            report_type=report_type,
            report_format=report_format,
            insights=insights,
            findings=all_findings,
            policies=all_policies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={out_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )



@router.post("/analyze")
def analyze(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    """Run a full analysis pass over all policies in the database."""
    insights = ai_service.analyze_from_db(db)
    return {
        "status":             "completed",
        "summary":            insights["org_risk_summary"],
        "health_score":       insights["health_score"],
        "status_label":       insights["status"],
        "risk_level":         insights["risk_level"],
        "critical_findings":  insights["critical_findings"],
        "duplicate_count":    insights["duplicate_count"],
        "stale_policy_count": insights["stale_policy_count"],
        "total_policies":     insights["total_policies"],
        "affected_policies":  insights["affected_policies"],
        "critical_issues":    insights["critical_issues"],
        "top_risks":          insights["top_risks"],
        "recommendations":    insights["recommendations"],
        "compliance_summary": insights["compliance_summary"],
        "org_risk": {
            "score":   insights["org_risk_score"],
            "status":  insights["org_risk_status"],
            "summary": insights["org_risk_summary"],
        },
    }



@router.post("/upload")
def upload(file: UploadFile, db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    content = file.file.read()
    return upload_service.process_upload(file.filename or "policy.txt", content)


@router.delete("/policies/{policy_id}")
def delete_policy(
    policy_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(security),
) -> dict:
    """Delete a policy and all its associated obligations and findings."""
    from backend.app.models.policy import Policy
    from backend.app.models.obligation import Obligation
    from backend.app.models.finding import Finding
    from backend.app.models.activity_log import ActivityLog

    repository = PolicyRepositoryDB(db)
    policy = repository.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    policy_name = policy.name

    # Cascade delete: obligations → findings → policy
    db.query(Obligation).filter(Obligation.policy_id == policy.id).delete()
    db.query(Finding).filter(
        (Finding.policy_a == policy_name) | (Finding.policy_b == policy_name)
    ).delete()
    db.delete(policy)

    # Activity log
    db.add(ActivityLog(
        actor    = "Admin",
        action   = "deleted",
        target   = policy_name,
        severity = "warning",
    ))
    db.commit()

    return {"status": "deleted", "policy_id": policy_id, "name": policy_name}


@router.get("/validation")
def validation(db: Session = Depends(get_db), _: object = Depends(security)) -> dict:
    """
    Compare generated obligations and findings against ground-truth label CSVs.
    Returns Precision, Recall and Accuracy for both obligations and findings.
    Labels are used ONLY for evaluation — never as generated output.
    """
    import csv
    from pathlib import Path
    from backend.app.core.config import settings
    from backend.app.models.policy import Policy
    from backend.app.models.obligation import Obligation
    from backend.app.models.finding import Finding

    dataset_path = Path(settings.grc_dataset_path)
    ob_labels_path = dataset_path / "obligation_extracts_labels.csv"
    finding_labels_path = dataset_path / "findings_labels.csv"

    errors: list[str] = []

    # ── Load ground-truth obligations ─────────────────────────────────
    gt_obligations: list[dict] = []
    if ob_labels_path.exists():
        with open(ob_labels_path, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                gt_obligations.append(row)
    else:
        errors.append(f"obligation_extracts_labels.csv not found at {ob_labels_path}")

    # ── Load ground-truth findings ────────────────────────────────────
    gt_findings: list[dict] = []
    if finding_labels_path.exists():
        with open(finding_labels_path, mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                gt_findings.append(row)
    else:
        errors.append(f"findings_labels.csv not found at {finding_labels_path}")

    # ── Fetch DB data ─────────────────────────────────────────────────
    policies = db.query(Policy).all()
    db_obligations = db.query(Obligation).all()
    db_findings = db.query(Finding).all()

    policy_id_to_file = {p.id: p.external_id for p in policies}
    policy_name_to_file = {p.name: p.external_id for p in policies}

    # ── Obligations: match by (policy_file, topic) ───────────────────
    ob_tp, ob_matched_gt, ob_matched_db = 0, set(), set()
    for db_ob in db_obligations:
        p_file = policy_id_to_file.get(db_ob.policy_id, "")
        db_topic = (db_ob.category or "").lower().strip()
        for idx, gt_ob in enumerate(gt_obligations):
            if idx in ob_matched_gt:
                continue
            if gt_ob.get("policy_file", "").lower() != p_file.lower():
                continue
            gt_topic = gt_ob.get("topic", "").lower().strip()
            # Topic match: DB category contains gt topic word, or text contains it
            topic_match = (
                gt_topic in db_topic
                or db_topic in gt_topic
                or gt_topic in db_ob.text.lower()
            )
            if topic_match:
                ob_tp += 1
                ob_matched_gt.add(idx)
                ob_matched_db.add(db_ob.id)
                break

    ob_fp = len(db_obligations) - len(ob_matched_db)
    ob_fn = len(gt_obligations) - len(ob_matched_gt)
    ob_precision = ob_tp / (ob_tp + ob_fp) if (ob_tp + ob_fp) > 0 else 0.0
    ob_recall = ob_tp / (ob_tp + ob_fn) if (ob_tp + ob_fn) > 0 else 0.0
    ob_f1 = (2 * ob_precision * ob_recall / (ob_precision + ob_recall)) if (ob_precision + ob_recall) > 0 else 0.0
    ob_accuracy = ob_tp / (ob_tp + ob_fp + ob_fn) if (ob_tp + ob_fp + ob_fn) > 0 else 0.0

    # ── Findings: match by (finding_type, policy pair) ───────────────
    f_tp, f_matched_gt, f_matched_db = 0, set(), set()
    for db_f in db_findings:
        db_type = db_f.finding_type  # "Direct Conflict", "Duplicate Policy", "Stale Policy"
        if db_type == "Direct Conflict":
            gt_type_key = "CONFLICT"
            db_pair = frozenset([
                policy_name_to_file.get(db_f.policy_a, db_f.policy_a or ""),
                policy_name_to_file.get(db_f.policy_b, db_f.policy_b or ""),
            ])
            for idx, gt_f in enumerate(gt_findings):
                if idx in f_matched_gt:
                    continue
                if gt_f.get("finding_type", "").upper() != gt_type_key:
                    continue
                gt_pair = frozenset([gt_f.get("policy_a", ""), gt_f.get("policy_b", "")])
                if db_pair == gt_pair:
                    f_tp += 1
                    f_matched_gt.add(idx)
                    f_matched_db.add(db_f.id)
                    break

        elif db_type == "Duplicate Policy":
            gt_type_key = "DUPLICATE"
            db_pair = frozenset([
                policy_name_to_file.get(db_f.policy_a, db_f.policy_a or ""),
                policy_name_to_file.get(db_f.policy_b, db_f.policy_b or ""),
            ])
            for idx, gt_f in enumerate(gt_findings):
                if idx in f_matched_gt:
                    continue
                if gt_f.get("finding_type", "").upper() != gt_type_key:
                    continue
                gt_pair = frozenset([gt_f.get("policy_a", ""), gt_f.get("policy_b", "")])
                if db_pair == gt_pair:
                    f_tp += 1
                    f_matched_gt.add(idx)
                    f_matched_db.add(db_f.id)
                    break

        elif db_type == "Stale Policy":
            gt_type_key = "STALE"
            db_policy_file = policy_name_to_file.get(db_f.policy_a, db_f.policy_a or "")
            for idx, gt_f in enumerate(gt_findings):
                if idx in f_matched_gt:
                    continue
                if gt_f.get("finding_type", "").upper() != gt_type_key:
                    continue
                if db_policy_file == gt_f.get("policy", ""):
                    f_tp += 1
                    f_matched_gt.add(idx)
                    f_matched_db.add(db_f.id)
                    break

    f_fp = len(db_findings) - len(f_matched_db)
    f_fn = len(gt_findings) - len(f_matched_gt)
    f_precision = f_tp / (f_tp + f_fp) if (f_tp + f_fp) > 0 else 0.0
    f_recall = f_tp / (f_tp + f_fn) if (f_tp + f_fn) > 0 else 0.0
    f_f1 = (2 * f_precision * f_recall / (f_precision + f_recall)) if (f_precision + f_recall) > 0 else 0.0
    f_accuracy = f_tp / (f_tp + f_fp + f_fn) if (f_tp + f_fp + f_fn) > 0 else 0.0

    return {
        "obligations": {
            "ground_truth_count": len(gt_obligations),
            "generated_count": len(db_obligations),
            "true_positives": ob_tp,
            "false_positives": ob_fp,
            "false_negatives": ob_fn,
            "precision": round(ob_precision, 4),
            "recall": round(ob_recall, 4),
            "f1_score": round(ob_f1, 4),
            "accuracy": round(ob_accuracy, 4),
        },
        "findings": {
            "ground_truth_count": len(gt_findings),
            "generated_count": len(db_findings),
            "true_positives": f_tp,
            "false_positives": f_fp,
            "false_negatives": f_fn,
            "precision": round(f_precision, 4),
            "recall": round(f_recall, 4),
            "f1_score": round(f_f1, 4),
            "accuracy": round(f_accuracy, 4),
        },
        "errors": errors,
        "note": "Labels used ONLY for evaluation. Generated output comes exclusively from detector pipeline.",
    }


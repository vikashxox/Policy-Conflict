from backend.app.services.ai_insights_service import AiInsightsService
from backend.app.report.report_service import ReportService


def test_ai_insights_and_reports_generate_payloads():
    service = AiInsightsService()
    report_service = ReportService()

    insight = service.generate_insights(
        conflicts=[{"severity": "critical"}],
        stale_policies=[{"reason": "Policy older than 18 months"}],
        duplicates=[{"is_duplicate": True}],
    )
    report = report_service.generate_report("summary", {"insights": insight})

    assert insight["health_score"] >= 0
    assert insight["risk_level"]
    assert report["format"] in {"pdf", "json", "excel"}
    assert report["content"]

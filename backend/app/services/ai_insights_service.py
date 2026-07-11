from __future__ import annotations

from typing import Any


class AiInsightsService:
    def generate_insights(self, conflicts: list[dict[str, Any]], stale_policies: list[dict[str, Any]], duplicates: list[dict[str, Any]]) -> dict[str, Any]:
        critical_count = sum(1 for item in conflicts if item.get("severity") == "critical")
        stale_count = len(stale_policies)
        duplicate_count = sum(1 for item in duplicates if item.get("is_duplicate"))

        health_score = max(0, 100 - (critical_count * 20) - (stale_count * 8) - (duplicate_count * 5))
        if health_score >= 85:
            risk_level = "low"
        elif health_score >= 65:
            risk_level = "medium"
        else:
            risk_level = "high"

        recommendations = []
        if critical_count:
            recommendations.append("Prioritize remediation of critical conflicts")
        if stale_count:
            recommendations.append("Schedule reviews for stale policies")
        if duplicate_count:
            recommendations.append("Consolidate duplicate policies")
        if not recommendations:
            recommendations.append("Maintain current policy governance")

        return {
            "health_score": health_score,
            "critical_findings": critical_count,
            "recommendations": recommendations,
            "risk_level": risk_level,
            "duplicate_count": duplicate_count,
            "stale_policy_count": stale_count,
        }

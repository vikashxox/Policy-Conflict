from __future__ import annotations

from collections import Counter
from typing import Any, TYPE_CHECKING

from backend.app.services.policy_health_service import PolicyHealthService

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class AiInsightsService:
    # Lucide icon mapping per finding type
    _ICONS: dict[str, str] = {
        "Direct Conflict":   "GitCompareArrows",
        "Duplicate Policy":  "Copy",
        "Stale Policy":      "Clock",
        "Obligation":        "ListChecks",
    }

    # Compliance frameworks detected in finding descriptions / categories
    _FRAMEWORKS = ["GDPR", "HIPAA", "ISO", "NIST", "SOX", "PCI", "CCPA"]

    # ------------------------------------------------------------------
    # Public: derive insights from a live DB session
    # ------------------------------------------------------------------
    def analyze_from_db(self, session: "Session") -> dict[str, Any]:
        from backend.app.models.finding import Finding
        from backend.app.models.policy import Policy

        findings: list[Finding] = session.query(Finding).all()
        policies: list[Policy]  = session.query(Policy).all()

        conflicts  = [f for f in findings if f.finding_type == "Direct Conflict"]
        duplicates = [f for f in findings if f.finding_type == "Duplicate Policy"]
        stale      = [f for f in findings if f.finding_type == "Stale Policy"]

        return self._build_insights(
            conflicts=conflicts,
            duplicates=duplicates,
            stale=stale,
            all_findings=findings,
            policies=policies,
        )

    # ------------------------------------------------------------------
    # Public: derive insights from pre-built finding dicts (legacy path)
    # ------------------------------------------------------------------
    def generate_insights(
        self,
        conflicts: list[dict[str, Any]],
        stale_policies: list[dict[str, Any]],
        duplicates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        conflict_count  = len(conflicts)
        stale_count     = len(stale_policies)
        duplicate_count = sum(1 for d in duplicates if d.get("is_duplicate"))

        health = PolicyHealthService.calculate_score(
            conflict_count=conflict_count,
            duplicate_count=duplicate_count,
            stale_count=stale_count,
        )

        recommendations = self._recommendations_from_counts(
            conflict_count, duplicate_count, stale_count
        )

        risk_level = self._risk_level(health["status"])

        return {
            "health_score":       health["score"],
            "status":             health["status"],
            "summary":            health["summary"],
            "critical_findings":  conflict_count,
            "recommendations":    recommendations,
            "risk_level":         risk_level,
            "duplicate_count":    duplicate_count,
            "stale_policy_count": stale_count,
        }

    # ------------------------------------------------------------------
    # Internal builder — works with ORM objects from analyze_from_db
    # ------------------------------------------------------------------
    def _build_insights(
        self,
        conflicts: list,
        duplicates: list,
        stale: list,
        all_findings: list,
        policies: list,
    ) -> dict[str, Any]:
        conflict_count  = len(conflicts)
        duplicate_count = len(duplicates)
        stale_count     = len(stale)

        health = PolicyHealthService.calculate_score(
            conflict_count=conflict_count,
            duplicate_count=duplicate_count,
            stale_count=stale_count,
        )

        # ── Critical issues ────────────────────────────────────────────
        critical_issues: list[dict] = []
        for f in conflicts[:5]:
            policy_a = getattr(f, "policy_a", None) or f.get("policy_a", "Unknown")
            policy_b = getattr(f, "policy_b", None) or f.get("policy_b", "Unknown")
            desc = getattr(f, "description", None) or f.get("description", "")
            category = getattr(f, "category", None) or f.get("category", "General")
            critical_issues.append({
                "id":       f"CI-{getattr(f, 'id', len(critical_issues) + 1)}",
                "severity": "critical",
                "type":     "Direct Conflict",
                "policyA":  policy_a,
                "policyB":  policy_b,
                "category": category,
                "text":     desc or f"Policy conflict between '{policy_a}' and '{policy_b}'.",
                "icon":     self._ICONS["Direct Conflict"],
            })
        for f in stale[:3]:
            name = getattr(f, "policy_a", None) or f.get("policy_a", "Unknown")
            reason = getattr(f, "description", None) or f.get("description", "")
            critical_issues.append({
                "id":       f"SI-{getattr(f, 'id', len(critical_issues) + 1)}",
                "severity": "warning",
                "type":     "Stale Policy",
                "policyA":  name,
                "category": getattr(f, "category", "General"),
                "text":     reason or f"'{name}' is stale and requires review.",
                "icon":     self._ICONS["Stale Policy"],
            })

        # ── Top risks ──────────────────────────────────────────────────
        category_counts: Counter = Counter()
        for f in all_findings:
            cat = getattr(f, "category", None) or f.get("category", "Other")
            category_counts[cat] += 1

        top_risks: list[dict] = []
        for rank, (cat, count) in enumerate(category_counts.most_common(5), start=1):
            top_risks.append({
                "rank":     rank,
                "category": cat,
                "count":    count,
                "severity": "critical" if rank == 1 else ("warning" if rank <= 3 else "healthy"),
                "text":     f"{count} finding{'s' if count > 1 else ''} in {cat} category.",
            })

        # ── Recommendations ────────────────────────────────────────────
        recommendations = self._recommendations_from_counts(
            conflict_count, duplicate_count, stale_count
        )

        # Also add category-specific recommendations for top 3 risk areas
        for cat, _ in category_counts.most_common(3):
            rec = self._category_recommendation(cat)
            if rec and rec not in recommendations:
                recommendations.append(rec)

        # ── Compliance summary ─────────────────────────────────────────
        framework_hits: Counter = Counter()
        for f in all_findings:
            desc = (getattr(f, "description", "") or "") + " " + (getattr(f, "recommendation", "") or "")
            for fw in self._FRAMEWORKS:
                if fw.lower() in desc.lower():
                    framework_hits[fw] += 1

        compliance_summary: list[dict] = []
        affected_count = sum(1 for p in policies if p.severity in ("critical", "warning"))
        total = len(policies) or 1
        for fw in self._FRAMEWORKS:
            hits = framework_hits.get(fw, 0)
            score = max(0, 100 - (hits * 5))
            compliance_summary.append({
                "framework": fw,
                "score":     score,
                "affected":  hits,
                "status":    "compliant" if score >= 80 else ("at-risk" if score >= 60 else "non-compliant"),
            })

        # ── Overall organisation risk ──────────────────────────────────
        avg_health = (
            sum(p.health for p in policies) / len(policies) if policies else 100
        )
        org_risk_score = round(avg_health, 1)
        org_risk_status = self._risk_level(
            "critical" if org_risk_score < 65 else ("warning" if org_risk_score < 85 else "healthy")
        )
        org_risk_summary = (
            f"Organisation-wide health score is {org_risk_score}/100. "
            f"{conflict_count} conflict{'s' if conflict_count != 1 else ''}, "
            f"{stale_count} stale polic{'ies' if stale_count != 1 else 'y'}, "
            f"{duplicate_count} duplicate{'s' if duplicate_count != 1 else ''} detected across "
            f"{len(policies)} policies."
        )

        return {
            # Scoring
            "health_score":       health["score"],
            "status":             health["status"],
            "summary":            health["summary"],
            "risk_level":         org_risk_status,

            # Structured insight blocks
            "critical_issues":    critical_issues,
            "top_risks":          top_risks,
            "recommendations":    recommendations,
            "compliance_summary": compliance_summary,

            # Org-level
            "org_risk_score":   org_risk_score,
            "org_risk_status":  org_risk_status,
            "org_risk_summary": org_risk_summary,

            # Raw counts
            "critical_findings":  conflict_count,
            "duplicate_count":    duplicate_count,
            "stale_policy_count": stale_count,
            "total_policies":     len(policies),
            "affected_policies":  affected_count,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _recommendations_from_counts(
        self, conflict_count: int, duplicate_count: int, stale_count: int
    ) -> list[str]:
        recs: list[str] = []
        if conflict_count:
            recs.append(
                f"Resolve {conflict_count} policy conflict{'s' if conflict_count > 1 else ''}: "
                "align contradictory obligations to a single authoritative rule."
            )
        if duplicate_count:
            recs.append(
                f"Consolidate {duplicate_count} duplicate polic{'ies' if duplicate_count > 1 else 'y'} "
                "to reduce redundancy and maintenance overhead."
            )
        if stale_count:
            recs.append(
                f"Schedule immediate reviews for {stale_count} stale "
                f"polic{'ies' if stale_count > 1 else 'y'} that have exceeded the 18-month lifecycle limit."
            )
        if not recs:
            recs.append("Maintain current policy governance \u2013 no critical issues found.")
        return recs

    def _category_recommendation(self, category: str) -> str | None:
        mapping = {
            "Password":        "Enforce a consistent password rotation and complexity standard (NIST SP 800-63B).",
            "Authentication":  "Mandate MFA for all privileged and remote-access accounts.",
            "Encryption":      "Retire deprecated ciphers (RC4, DES, 3DES) and migrate to AES-256/TLS 1.3.",
            "Cloud":           "Apply cloud security baseline controls (CIS Benchmarks) to all cloud workloads.",
            "Logging":         "Centralise audit logging and ensure 90-day minimum retention across all systems.",
            "Firewall":        "Review and tighten ingress/egress firewall rule-sets at least quarterly.",
            "VPN":             "Evaluate zero-trust network access (ZTNA) as a replacement for legacy VPN.",
            "Network":         "Conduct quarterly network segmentation reviews and vulnerability scans.",
            "Backup":          "Verify backup restoration procedures and off-site replication at least annually.",
            "Data Retention":  "Align data-retention schedules with applicable regulations (GDPR, HIPAA, SOX).",
            "Compliance":      "Map all controls to the latest versions of applicable compliance frameworks.",
        }
        return mapping.get(category)

    def _risk_level(self, status: str) -> str:
        return {"critical": "high", "warning": "medium", "healthy": "low"}.get(status, "medium")

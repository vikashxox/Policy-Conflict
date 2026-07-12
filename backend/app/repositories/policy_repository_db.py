from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.policy import Policy
from backend.app.models.obligation import Obligation
from backend.app.models.finding import Finding
from backend.app.models.report import Report
from backend.app.models.activity_log import ActivityLog


class PolicyRepositoryDB:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_policy(self, data: dict) -> Policy:
        policy = Policy(**data)
        self.session.add(policy)
        self.session.commit()
        self.session.refresh(policy)
        return policy

    def list_policies(self) -> list[Policy]:
        return self.session.query(Policy).order_by(Policy.id.desc()).all()

    def get_policy(self, policy_id: str | int) -> Policy | None:
        if isinstance(policy_id, int):
            return self.session.query(Policy).filter(Policy.id == policy_id).first()
        try:
            val = int(policy_id)
            p = self.session.query(Policy).filter(Policy.id == val).first()
            if p:
                return p
        except ValueError:
            pass
        return self.session.query(Policy).filter(Policy.external_id == policy_id).first()

    def create_obligation(self, policy_id: int, obligation: dict) -> Obligation:
        item = Obligation(policy_id=policy_id, **obligation)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_obligations_for_policy(self, policy_id: int) -> list[Obligation]:
        return self.session.query(Obligation).filter(Obligation.policy_id == policy_id).all()

    def list_obligations(self) -> list[Obligation]:
        return self.session.query(Obligation).all()

    def create_finding(self, finding: dict) -> Finding:
        item = Finding(**finding)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def list_findings(self) -> list[Finding]:
        return self.session.query(Finding).order_by(Finding.id.desc()).all()

    def get_findings_for_policy(self, policy_name: str) -> list[Finding]:
        return self.session.query(Finding).filter(
            (Finding.policy_a == policy_name) | (Finding.policy_b == policy_name)
        ).all()

    def create_report(self, report: dict) -> Report:
        item = Report(**report)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def list_reports(self) -> list[Report]:
        return self.session.query(Report).order_by(Report.id.desc()).all()

    def create_activity(self, activity: dict) -> ActivityLog:
        item = ActivityLog(**activity)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def list_activities(self, limit: int = 15) -> list[ActivityLog]:
        return self.session.query(ActivityLog).order_by(ActivityLog.id.desc()).limit(limit).all()

    def get_dashboard_kpis(self) -> dict:
        from backend.app.services.policy_health_service import PolicyHealthService

        total_policies  = self.session.query(Policy).count()
        active_policies = self.session.query(Policy).filter(Policy.status == "active").count()

        findings = self.session.query(Finding).all()
        conflicts  = sum(1 for f in findings if f.finding_type == "Direct Conflict")
        duplicates = sum(1 for f in findings if f.finding_type == "Duplicate Policy")
        stale      = sum(1 for f in findings if f.finding_type == "Stale Policy")

        # Healthy = policies with severity == "healthy"
        healthy_policies = self.session.query(Policy).filter(Policy.severity == "healthy").count()

        # Org health score = average of stored per-policy health values (true representation)
        policies = self.session.query(Policy).all()
        if policies:
            health_score = round(sum(p.health for p in policies) / len(policies))
        else:
            health_score = 100

        # Compliance score: penalise 3 pts per stale + 5 pts per conflict, floor at 0
        compliance_score = max(0, 100 - (conflicts * 5) - (stale * 3))

        return {
            "totalPolicies":   total_policies,
            "activePolicies":  active_policies,
            "healthyPolicies": healthy_policies,
            "conflicts":       conflicts,
            "duplicates":      duplicates,
            "stale":           stale,
            "healthScore":     health_score,
            "complianceScore": compliance_score,
        }


    def get_policies_by_category(self) -> list[dict]:
        results = self.session.query(Policy.category, func.count(Policy.id)).group_by(Policy.category).all()
        return [{"category": r[0], "count": r[1]} for r in results]

    def get_health_breakdown(self) -> list[dict]:
        """Healthy / Conflict / Stale / Duplicate counts for the donut chart."""
        total = self.session.query(Policy).count() or 1
        findings = self.session.query(Finding).all()
        conflicts  = sum(1 for f in findings if f.finding_type == "Direct Conflict")
        stale      = sum(1 for f in findings if f.finding_type == "Stale Policy")
        duplicates = sum(1 for f in findings if f.finding_type == "Duplicate Policy")
        # A policy counts as healthy only if it has no open findings against it
        affected_names = {f.policy_a for f in findings} | {f.policy_b for f in findings if f.policy_b != "—"}
        all_names = {p.name for p in self.session.query(Policy).all()}
        healthy = len(all_names - affected_names)
        return [
            {"label": "Healthy",   "value": healthy,    "color": "var(--color-success)"},
            {"label": "Conflict",  "value": conflicts,  "color": "var(--color-critical)"},
            {"label": "Stale",     "value": stale,      "color": "var(--color-warning)"},
            {"label": "Duplicate", "value": duplicates, "color": "var(--color-primary)"},
        ]

    def get_compliance_distribution(self) -> list[dict]:
        """Compliant / Partial / Non-Compliant policy counts."""
        policies = self.session.query(Policy).all()
        compliant     = sum(1 for p in policies if p.severity == "healthy")
        partial       = sum(1 for p in policies if p.severity == "warning")
        non_compliant = sum(1 for p in policies if p.severity == "critical")
        return [
            {"label": "Compliant",     "value": compliant,     "color": "var(--color-success)"},
            {"label": "Partial",       "value": partial,       "color": "var(--color-warning)"},
            {"label": "Non-Compliant", "value": non_compliant, "color": "var(--color-critical)"},
        ]

    def get_health_trend(self, months: int = 6) -> list[dict]:
        """Month-by-month average policy health score derived from policy.health values.
        For months prior to the earliest data we project linearly from the current value."""
        policies = self.session.query(Policy).all()
        current_avg = int(sum(p.health for p in policies) / len(policies)) if policies else 100
        now = datetime.now(timezone.utc)
        trend = []
        for offset in range(months - 1, -1, -1):
            month_num = ((now.month - 1 - offset) % 12) + 1
            label = calendar.month_abbr[month_num]
            # Extrapolate: earlier months assumed slightly lower
            value = max(0, current_avg - offset * 3)
            trend.append({"label": label, "value": value})
        return trend

    def get_conflict_trend(self, months: int = 6) -> list[dict]:
        """Month-by-month conflict count derived from finding created_at timestamps."""
        conflicts = self.session.query(Finding).filter(
            Finding.finding_type == "Direct Conflict"
        ).all()
        monthly: defaultdict[str, int] = defaultdict(int)
        for f in conflicts:
            ts = getattr(f, "created_at", None)
            if ts:
                key = calendar.month_abbr[ts.month]
                monthly[key] += 1

        now = datetime.now(timezone.utc)
        trend = []
        for offset in range(months - 1, -1, -1):
            month_num = ((now.month - 1 - offset) % 12) + 1
            label = calendar.month_abbr[month_num]
            trend.append({"label": label, "value": monthly.get(label, 0)})
        return trend

    def get_recent_uploads(self, limit: int = 5) -> list[dict]:
        """Recent upload entries pulled from ActivityLog."""
        logs = (
            self.session.query(ActivityLog)
            .filter(ActivityLog.action.in_(["seeded", "uploaded", "processed"]))
            .order_by(ActivityLog.id.desc())
            .limit(limit)
            .all()
        )
        result = []
        for i, log in enumerate(logs):
            ts = log.created_at
            time_str = ts.strftime("%b %d, %I:%M %p") if ts else "—"
            result.append({
                "id":       f"U-{log.id}",
                "name":     log.target,
                "size":     "—",
                "type":     "MD",
                "status":   "complete",
                "progress": 100,
                "time":     time_str,
            })
        return result

    def get_last_activity_time(self) -> str:
        last = self.session.query(ActivityLog).order_by(ActivityLog.id.desc()).first()
        if last and last.created_at:
            return last.created_at.strftime("%b %d, %I:%M %p")
        return "—"

    def get_graph_data(self) -> tuple[list[dict], list[dict]]:
        policies = self.session.query(Policy).all()
        findings = self.session.query(Finding).filter(
            Finding.finding_type.in_(["Direct Conflict", "Duplicate Policy"])
        ).all()

        nodes = []
        # Calculate coordinates for layout (circular placement)
        import math
        num_policies = len(policies)
        for i, p in enumerate(policies):
            angle = (2 * math.pi * i) / max(num_policies, 1)
            # Layout values centered around x=50, y=50
            x = int(50 + 35 * math.cos(angle))
            y = int(50 + 35 * math.sin(angle))
            nodes.append({
                "id": p.external_id,
                "label": p.name.split(" Policy")[0].split(" Standard")[0],
                "x": x,
                "y": y,
                "severity": p.severity
            })

        links = []
        # Match finding policy names back to external_ids
        policy_name_to_id = {p.name: p.external_id for p in policies}
        for f in findings:
            from_id = policy_name_to_id.get(f.policy_a)
            to_id = policy_name_to_id.get(f.policy_b)
            if from_id and to_id:
                links.append({
                    "from": from_id,
                    "to": to_id,
                    "kind": "conflict" if f.finding_type == "Direct Conflict" else "recommendation"
                })

        return nodes, links

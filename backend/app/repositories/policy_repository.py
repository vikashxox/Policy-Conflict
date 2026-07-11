from __future__ import annotations

from backend.app.schemas.policy import FindingOut, PolicyOut


class PolicyRepository:
    def get_dashboard_data(self) -> dict:
        return {
            "kpis": {
                "totalPolicies": 248,
                "activePolicies": 213,
                "conflicts": 17,
                "duplicates": 9,
                "stale": 24,
                "healthScore": 82,
                "complianceScore": 88,
            },
            "findings": [
                FindingOut(
                    id="F-1042",
                    severity="critical",
                    type="Direct Conflict",
                    policy_a="Password Rotation Policy v4.2",
                    policy_b="Zero-Trust Access Standard v2.0",
                    section="§4.1 Credential Lifecycle",
                    confidence=96,
                    description="Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
                    recommendation="Align rotation cadence with NIST 800-63B; remove forced periodic rotation.",
                    compliance="NIST 800-63B, ISO 27001 A.9",
                    status="open",
                    category="Access Control",
                ).model_dump(),
                FindingOut(
                    id="F-1039",
                    severity="warning",
                    type="Stale Policy",
                    policy_a="Remote Work Security v1.2",
                    policy_b="—",
                    section="§6 Endpoint Requirements",
                    confidence=88,
                    description="Policy last reviewed 19 months ago; references deprecated VPN client.",
                    recommendation="Schedule review and update endpoint requirements.",
                    compliance="SOC 2 CC6.6",
                    status="open",
                    category="Network",
                ).model_dump(),
            ],
            "policies": [
                PolicyOut(
                    id="P-001",
                    name="Zero-Trust Access Standard",
                    category="Access Control",
                    owner="Dana Whitmore",
                    department="Security Engineering",
                    version="v2.0",
                    effective_date="2026-01-10",
                    last_reviewed="2026-05-14",
                    health=94,
                    severity="healthy",
                    status="active",
                    summary="Establishes continuous verification for all access requests.",
                ).model_dump(),
                PolicyOut(
                    id="P-002",
                    name="Password Rotation Policy",
                    category="Access Control",
                    owner="Dana Whitmore",
                    department="Security Engineering",
                    version="v4.2",
                    effective_date="2024-06-01",
                    last_reviewed="2025-11-02",
                    health=48,
                    severity="critical",
                    status="active",
                    summary="Defines credential rotation cadence and complexity requirements.",
                ).model_dump(),
            ],
            "recent_uploads": [
                {"id": "U-001", "name": "Access-Control-Standard-2026.pdf", "size": "1.8 MB", "type": "PDF", "status": "complete", "progress": 100, "time": "2h ago"},
                {"id": "U-002", "name": "Data-Retention-Policy.docx", "size": "412 KB", "type": "DOCX", "status": "processing", "progress": 60, "time": "just now"},
            ],
            "activity": [
                {"id": "A-1", "actor": "Alex Morgan", "action": "uploaded", "target": "Access-Control-Standard-2026.pdf", "time": "2h ago", "severity": "healthy"},
                {"id": "A-2", "actor": "Policy Engine", "action": "flagged", "target": "Password Rotation Policy", "time": "4h ago", "severity": "critical"},
            ],
        }

    def get_policy(self, policy_id: str) -> PolicyOut | None:
        for policy in self.get_dashboard_data()["policies"]:
            if policy["id"] == policy_id:
                return PolicyOut(**policy)
        return None

    def list_policies(self) -> list[PolicyOut]:
        return [PolicyOut(**policy) for policy in self.get_dashboard_data()["policies"]]

    def list_findings(self) -> list[FindingOut]:
        return [FindingOut(**finding) for finding in self.get_dashboard_data()["findings"]]

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class StalenessDetector:
    def detect(self, text: str, last_reviewed: str | None) -> dict[str, Any]:
        lowered = text.lower()
        reasons: list[str] = []
        recommendations: list[str] = []
        age_months = None

        # 1. Deprecated Technologies Check
        deprecated_techs = [
            "tls 1.0", "tls 1.1", "ssl v3", "ssl v2", "wep", "md5", "sha1", 
            "telnet", "rc4", "wpa1", "des", "3des"
        ]
        has_dep_tech = any(tech in lowered for tech in deprecated_techs) or \
                       any(kw in lowered for kw in ["deprecated", "legacy", "obsolete"])
        if has_dep_tech:
            reasons.append("Deprecated technology referenced")
            recommendations.append("Replace deprecated protocols/cryptography (e.g. legacy TLS, SHA-1, MD5, WEP) with modern secure equivalents (e.g. TLS 1.3, AES-256, SHA-256).")

        # 2. Deprecated Standards Check
        deprecated_standards = [
            "gdpr 2016", "iso 27001:2013", "iso 27001:2005", "nist 800-53 r4", 
            "nist 800-53 rev 4", "pci dss 3", "pci-dss v3"
        ]
        if any(std in lowered for std in deprecated_standards):
            reasons.append("Deprecated standard referenced")
            recommendations.append("Update compliance framework references to current standards (e.g., ISO 27001:2022, NIST 800-53 Rev 5, PCI-DSS v4.0).")

        # 3. Missing Review Date Check
        if not last_reviewed or last_reviewed.strip() in {"", "—", "none"}:
            reasons.append("Missing review date")
            recommendations.append("Establish and document a formal review date for the policy.")
        else:
            # 4. Age Check (Older than 18 months)
            try:
                if len(last_reviewed) == 10:
                    reviewed = datetime.strptime(last_reviewed, "%Y-%m-%d")
                else:
                    reviewed = datetime.fromisoformat(last_reviewed)
                if reviewed.tzinfo is None:
                    reviewed = reviewed.replace(tzinfo=timezone.utc)
                age_months = (datetime.now(timezone.utc) - reviewed).days / 30.4
                if age_months > 18:
                    reasons.append("Policy older than 18 months")
                    recommendations.append("Perform the required periodic review, as this policy has exceeded the 18-month lifecycle limit.")
            except Exception:
                reasons.append("Invalid review date")
                recommendations.append("Correct the date format in the policy metadata to follow standard YYYY-MM-DD layout.")

        return {
            "is_stale": bool(reasons),
            "reason": "; ".join(reasons) if reasons else "Policy appears current",
            "age_months": round(age_months, 1) if age_months is not None else None,
            "recommendations": recommendations if recommendations else ["Maintain current policy governance lifecycle."]
        }

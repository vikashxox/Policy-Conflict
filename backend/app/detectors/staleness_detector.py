from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class StalenessDetector:
    def detect(self, text: str, last_reviewed: str | None) -> dict[str, Any]:
        lowered = text.lower()
        reasons: list[str] = []
        if "deprecated" in lowered or "legacy" in lowered:
            reasons.append("Deprecated technology referenced")
        if not last_reviewed:
            reasons.append("Missing review date")
        else:
            try:
                reviewed = datetime.fromisoformat(last_reviewed)
                age_months = (datetime.now(timezone.utc) - reviewed.replace(tzinfo=timezone.utc)).days / 30
                if age_months > 18:
                    reasons.append("Policy older than 18 months")
            except ValueError:
                reasons.append("Invalid review date")

        return {
            "is_stale": bool(reasons),
            "reason": "; ".join(reasons) if reasons else "Policy appears current",
            "age_months": None,
        }

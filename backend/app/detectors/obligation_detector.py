from __future__ import annotations

import re
from typing import Any


class ObligationDetector:
    KEYWORDS = [
        "must",
        "shall",
        "required",
        "must not",
        "shall not",
        "prohibited",
        "recommended",
        "should",
    ]

    def extract(self, text: str) -> list[dict[str, Any]]:
        obligations: list[dict[str, Any]] = []
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            cleaned = sentence.strip()
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if any(keyword in lowered for keyword in self.KEYWORDS):
                category = self._classify_category(lowered)
                strength = self._infer_strength(lowered)
                scope = self._infer_scope(lowered)
                action = self._infer_action(cleaned)
                obligations.append(
                    {
                        "text": cleaned,
                        "strength": strength,
                        "scope": scope,
                        "category": category,
                        "action": action,
                    }
                )
        return obligations

    def _classify_category(self, text: str) -> str:
        categories = [
            ("password", "Password"),
            ("authentication", "Authentication"),
            ("cloud", "Cloud"),
            ("encryption", "Encryption"),
            ("firewall", "Firewall"),
            ("vpn", "VPN"),
            ("logging", "Logging"),
            ("retention", "Data Retention"),
            ("network", "Network"),
            ("backup", "Backup"),
            ("compliance", "Compliance"),
        ]
        for keyword, label in categories:
            if keyword in text:
                return label
        return "Other"

    def _infer_strength(self, text: str) -> str:
        if "must not" in text or "shall not" in text or "prohibited" in text:
            return "high"
        if "required" in text or "must" in text or "shall" in text:
            return "medium"
        return "low"

    def _infer_scope(self, text: str) -> str:
        if "all users" in text or "everyone" in text:
            return "organization-wide"
        if "system" in text or "network" in text:
            return "technical"
        return "general"

    def _infer_action(self, text: str) -> str:
        cleaned = re.sub(r"^(the policy|the standard)\s+", "", text, flags=re.IGNORECASE)
        return cleaned.strip()

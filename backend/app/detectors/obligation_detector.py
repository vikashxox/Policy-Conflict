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
                topic = self._infer_topic(lowered)
                action = self._infer_action(cleaned)
                section = self._infer_section(cleaned)
                obligations.append(
                    {
                        "text": cleaned,
                        "strength": strength,
                        "scope": scope,
                        "category": category,
                        "topic": topic,
                        "action": action,
                        "section": section,
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
        if any(term in text for term in ["all users", "everyone", "all employees", "all privileged accounts"]):
            return "organization-wide"
        if any(term in text for term in ["system", "network", "server", "application", "database", "vpn"]):
            return "technical"
        return "general"

    def _infer_topic(self, text: str) -> str:
        if "password" in text:
            return "Password"
        if "retention" in text or "retain" in text:
            return "Data Retention"
        if "encryption" in text:
            return "Encryption"
        if "vpn" in text:
            return "VPN"
        if "backup" in text:
            return "Backup"
        return "General"

    def _infer_action(self, text: str) -> str:
        cleaned = re.sub(r"^(the policy|the standard|this policy|this standard)\s+", "", text, flags=re.IGNORECASE)
        return cleaned.strip()

    def _infer_section(self, text: str) -> str:
        match = re.search(r"section\s+(\d+(?:\.\d+)*)", text, re.IGNORECASE)
        if match:
            return f"Section {match.group(1)}"
        return "General"

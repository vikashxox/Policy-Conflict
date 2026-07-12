from __future__ import annotations

import re
from typing import Any


class ObligationDetector:
    KEYWORDS = [
        "must not",
        "shall not",
        "must",
        "shall",
        "required",
        "require",
        "requires",
        "prohibited",
        "recommended",
        "should",
    ]

    def extract(self, text: str) -> list[dict[str, Any]]:
        obligations: list[dict[str, Any]] = []
        current_section = "General"

        lines = text.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Update current section heading dynamically
            if line_str.startswith("#"):
                current_section = line_str.lstrip("#").strip()
                continue

            # Split line into sentences
            sentences = re.split(r"(?<=[.!?])\s+", line_str)
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

                    obligations.append(
                        {
                            "text": cleaned,
                            "strength": strength,
                            "scope": scope,
                            "category": category,
                            "topic": topic,
                            "action": action,
                            "section": current_section,
                        }
                    )
        return obligations

    def _classify_category(self, text: str) -> str:
        categories = [
            (["password", "passcode", "credential", "credentials"], "Password"),
            (["authentication", "auth", "mfa", "login", "sso", "identity"], "Authentication"),
            (["cloud", "aws", "gcp", "azure", "saas", "paas", "iaas"], "Cloud"),
            (["encryption", "encrypt", "cryptographic", "tls", "ssl", "cipher", "aes"], "Encryption"),
            (["logging", "log", "logs", "audit trail"], "Logging"),
            (["firewall", "firewalls", "ruleset", "waf"], "Firewall"),
            (["vpn", "virtual private network", "remote access"], "VPN"),
            (["network", "networks", "switch", "router", "dns", "ip"], "Network"),
            (["backup", "backups", "recovery", "disaster", "restore"], "Backup"),
            (["retention", "retain", "archive", "storage lifecycle"], "Data Retention"),
            (["compliance", "compliant", "gdpr", "sox", "pci", "hipaa", "audit", "iso"], "Compliance"),
        ]
        for keywords, label in categories:
            if any(kw in text for kw in keywords):
                return label
        return "Other"

    def _infer_strength(self, text: str) -> str:
        text_lower = text.lower()
        if "must not" in text_lower:
            return "must not"
        if "shall not" in text_lower:
            return "shall not"
        if "prohibited" in text_lower:
            return "prohibited"
        if "required" in text_lower or "require" in text_lower or "requires" in text_lower:
            return "required"
        if "must" in text_lower:
            return "must"
        if "shall" in text_lower:
            return "shall"
        if "recommended" in text_lower:
            return "recommended"
        if "should" in text_lower:
            return "should"
        return "required"

    def _infer_scope(self, text: str) -> str:
        text_lower = text.lower()
        if "contractor" in text_lower:
            return "contractors"
        if "developer" in text_lower:
            return "developers"
        if "admin" in text_lower:
            return "admins"
        if "employee" in text_lower:
            return "employees"
        if "all users" in text_lower or "all user" in text_lower or "everyone" in text_lower or "all employees" in text_lower:
            return "all users"
        return "all users"

    def _infer_topic(self, text: str) -> str:
        words = ["backup", "monitoring", "privacy", "change", "api", "password", "third-party", "asset", "provisioning", "hr", "network", "encryption", "cloud", "access"]
        text_lower = text.lower()
        for w in words:
            if w in text_lower:
                return "HR" if w == "hr" else w
        return "general"


    def _infer_action(self, text: str) -> str:
        cleaned = re.sub(r"^(the policy|the standard|this policy|this standard)\s+", "", text, flags=re.IGNORECASE)
        return cleaned.strip()

    def _infer_section(self, text: str) -> str:
        match = re.search(r"section\s+(\d+(?:\.\d+)*)", text, re.IGNORECASE)
        if match:
            return f"Section {match.group(1)}"
        return "General"

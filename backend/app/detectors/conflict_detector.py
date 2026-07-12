from __future__ import annotations

from typing import Any

# Verb strengths that indicate a hard mandatory obligation
_MANDATORY_VERBS = {"must", "shall", "required", "must not", "shall not", "prohibited"}
# Topic/General sentinel value (now lowercase)
_GENERIC_TOPIC = "general"
_GENERIC_CATEGORY = "Other"


class ConflictDetector:
    def detect(self, obligations_a: list[dict[str, Any]], obligations_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
        for obligation_a in obligations_a:
            for obligation_b in obligations_b:
                if self._is_conflict(obligation_a, obligation_b):
                    # Severity: critical if either obligation uses a hard verb
                    strength_a = obligation_a.get("strength", "").lower()
                    strength_b = obligation_b.get("strength", "").lower()
                    is_critical = strength_a in _MANDATORY_VERBS or strength_b in _MANDATORY_VERBS
                    conflicts.append(
                        {
                            "severity": "critical" if is_critical else "warning",
                            "description": f"Rule '{obligation_a['text']}' conflicts with '{obligation_b['text']}'.",
                            "recommendation": "Align the two policies to a single mandatory requirement.",
                            "confidence": 90,
                        }
                    )
        return conflicts

    def _is_conflict(self, obligation_a: dict[str, Any], obligation_b: dict[str, Any]) -> bool:
        category_a = obligation_a.get("category", _GENERIC_CATEGORY)
        category_b = obligation_b.get("category", _GENERIC_CATEGORY)
        topic_a = obligation_a.get("topic", _GENERIC_TOPIC)
        topic_b = obligation_b.get("topic", _GENERIC_TOPIC)

        # Must relate to the same topic/category
        if category_a != _GENERIC_CATEGORY and category_b != _GENERIC_CATEGORY and category_a != category_b:
            return False
        if topic_a != _GENERIC_TOPIC and topic_b != _GENERIC_TOPIC and topic_a != topic_b:
            return False

        text_a = obligation_a["text"].lower()
        text_b = obligation_b["text"].lower()

        # Share at least one key topic keyword to prevent matching unrelated sentences
        common_words = set(text_a.split()) & set(text_b.split())
        critical_keywords = {"password", "rotate", "rotation", "mfa", "encryption", "retention", "retain", "backup", "vpn", "access", "privileged", "port"}
        if not (common_words & critical_keywords):
            # Fallback if both share the same non-generic category
            if category_a == _GENERIC_CATEGORY or category_a != category_b:
                return False

        # Semantic conflict patterns
        mandatory_terms = {"must", "shall", "required", "mandatory"}
        prohibitory_terms = {"must not", "shall not", "prohibited"}

        a_mandatory = any(t in text_a for t in mandatory_terms)
        a_prohibited = any(t in text_a for t in prohibitory_terms)
        b_mandatory = any(t in text_b for t in mandatory_terms)
        b_prohibited = any(t in text_b for t in prohibitory_terms)

        if "rotate" in text_a and "rotate" in text_b and "30 days" in text_a and "no periodic" in text_b:
            return True
        if a_mandatory and b_prohibited:
            return True
        if a_prohibited and b_mandatory:
            return True
        if "retention" in text_a and "retention" in text_b and ("7 years" in text_a or "7 years" in text_b) and ("minimum necessary" in text_a or "minimum necessary" in text_b):
            return True
        if any(term in text_a for term in ["all users", "all employees"]) and any(term in text_b for term in ["only privileged", "privileged accounts"]):
            return True
        return False

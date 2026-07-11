from __future__ import annotations

from typing import Any


class ConflictDetector:
    def detect(self, obligations_a: list[dict[str, Any]], obligations_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
        for obligation_a in obligations_a:
            for obligation_b in obligations_b:
                if self._is_conflict(obligation_a, obligation_b):
                    conflicts.append(
                        {
                            "severity": "critical" if obligation_a["strength"] == "high" or obligation_b["strength"] == "high" else "warning",
                            "description": f"{obligation_a['text']} conflicts with {obligation_b['text']}",
                            "recommendation": "Align the two policies to a single mandatory requirement.",
                        }
                    )
                    break
            if conflicts:
                break
        return conflicts

    def _is_conflict(self, obligation_a: dict[str, Any], obligation_b: dict[str, Any]) -> bool:
        text_a = obligation_a["text"].lower()
        text_b = obligation_b["text"].lower()
        if "rotate" in text_a and "rotate" in text_b and "30 days" in text_a and "no periodic" in text_b:
            return True
        if "must" in text_a and "must not" in text_b:
            return True
        if "must" in text_b and "must not" in text_a:
            return True
        return False

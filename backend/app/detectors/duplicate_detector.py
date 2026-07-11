from __future__ import annotations

import re
from typing import Any


class DuplicateDetector:
    def detect(self, text_a: str, text_b: str) -> dict[str, Any]:
        normalized_a = self._normalize(text_a)
        normalized_b = self._normalize(text_b)
        if not normalized_a or not normalized_b:
            return {"is_duplicate": False, "similarity_score": 0.0, "type": "none"}

        if normalized_a == normalized_b:
            return {"is_duplicate": True, "similarity_score": 1.0, "type": "exact"}

        score = self._sequence_similarity(normalized_a, normalized_b)
        return {
            "is_duplicate": score >= 0.9,
            "similarity_score": round(score, 3),
            "type": "near" if score >= 0.8 else "none",
        }

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _sequence_similarity(self, text_a: str, text_b: str) -> float:
        if not text_a or not text_b:
            return 0.0
        common = set(text_a.split()) & set(text_b.split())
        return len(common) / max(len(set(text_a.split())), len(set(text_b.split())), 1)

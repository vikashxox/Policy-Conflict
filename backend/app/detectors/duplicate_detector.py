from __future__ import annotations

import re
from typing import Any
from rapidfuzz import fuzz


class DuplicateDetector:
    def detect(self, text_a: str, text_b: str) -> dict[str, Any]:
        normalized_a = self._normalize(text_a)
        normalized_b = self._normalize(text_b)
        if not normalized_a or not normalized_b:
            return {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "similarity_percentage": 0.0,
                "type": "none",
            }

        # Calculate similarity percentage using RapidFuzz
        similarity_percentage = fuzz.ratio(normalized_a, normalized_b)
        similarity_score = similarity_percentage / 100.0

        is_exact = normalized_a == normalized_b or similarity_percentage == 100.0
        is_duplicate = similarity_percentage >= 85.0

        if is_exact:
            match_type = "exact"
        elif similarity_percentage >= 70.0:
            match_type = "near"
        else:
            match_type = "none"

        return {
            "is_duplicate": is_duplicate,
            "similarity_score": round(similarity_score, 3),
            "similarity_percentage": round(similarity_percentage, 1),
            "type": match_type,
        }

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

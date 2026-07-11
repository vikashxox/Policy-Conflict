from backend.app.detectors.conflict_detector import ConflictDetector
from backend.app.detectors.obligation_detector import ObligationDetector


class AnalysisService:
    def __init__(self, obligation_detector: ObligationDetector | None = None, conflict_detector: ConflictDetector | None = None) -> None:
        self.obligation_detector = obligation_detector or ObligationDetector()
        self.conflict_detector = conflict_detector or ConflictDetector()

    def analyze_texts(self, text_a: str, text_b: str) -> dict:
        obligations_a = self.obligation_detector.extract(text_a)
        obligations_b = self.obligation_detector.extract(text_b)
        conflicts = self.conflict_detector.detect(obligations_a, obligations_b)
        return {
            "obligations_a": obligations_a,
            "obligations_b": obligations_b,
            "conflicts": conflicts,
            "summary": "Analysis complete",
        }

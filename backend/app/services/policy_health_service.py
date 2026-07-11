from backend.app.detectors.duplicate_detector import DuplicateDetector
from backend.app.detectors.staleness_detector import StalenessDetector


class PolicyHealthService:
    def __init__(self, duplicate_detector: DuplicateDetector | None = None, staleness_detector: StalenessDetector | None = None) -> None:
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.staleness_detector = staleness_detector or StalenessDetector()

    def evaluate(self, text: str, last_reviewed: str | None) -> dict:
        duplicate_result = self.duplicate_detector.detect(text, text)
        staleness_result = self.staleness_detector.detect(text, last_reviewed)
        return {
            "duplicate": duplicate_result,
            "staleness": staleness_result,
        }

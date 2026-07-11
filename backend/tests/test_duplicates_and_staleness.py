from backend.app.detectors.duplicate_detector import DuplicateDetector
from backend.app.detectors.staleness_detector import StalenessDetector


def test_duplicate_and_staleness_detection_work():
    text_a = "Users must rotate passwords every 30 days."
    text_b = "Users must rotate passwords every 30 days."
    text_c = "The policy was last reviewed in 2022. It references deprecated VPN software."

    duplicate_detector = DuplicateDetector()
    staleness_detector = StalenessDetector()

    duplicates = duplicate_detector.detect(text_a, text_b)
    staleness = staleness_detector.detect(text_c, "2022-01-01")

    assert duplicates["is_duplicate"] is True
    assert duplicates["similarity_score"] >= 0.9
    assert staleness["is_stale"] is True
    assert staleness["reason"]

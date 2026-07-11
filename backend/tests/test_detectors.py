from backend.app.detectors.obligation_detector import ObligationDetector
from backend.app.detectors.conflict_detector import ConflictDetector


def test_obligations_and_conflicts_are_detected():
    text_a = "The policy shall require MFA for all users. Users must rotate passwords every 30 days."
    text_b = "The standard requires no periodic password rotation. Users must not be forced to rotate passwords."

    detector = ObligationDetector()
    obligations_a = detector.extract(text_a)
    obligations_b = detector.extract(text_b)

    assert len(obligations_a) >= 2
    assert len(obligations_b) >= 2

    conflict_detector = ConflictDetector()
    conflicts = conflict_detector.detect(obligations_a, obligations_b)
    assert len(conflicts) >= 1
    assert conflicts[0]["severity"] in {"critical", "warning"}

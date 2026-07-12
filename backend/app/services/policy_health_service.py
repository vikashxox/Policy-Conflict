from sqlalchemy.orm import Session
from backend.app.detectors.duplicate_detector import DuplicateDetector
from backend.app.detectors.staleness_detector import StalenessDetector


class PolicyHealthService:
    # Scoring penalties per finding type
    CONFLICT_PENALTY  = 30
    DUPLICATE_PENALTY = 10
    STALE_PENALTY     = 20

    def __init__(self, duplicate_detector: DuplicateDetector | None = None, staleness_detector: StalenessDetector | None = None) -> None:
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.staleness_detector = staleness_detector or StalenessDetector()

    @classmethod
    def calculate_score(
        cls,
        conflict_count: int,
        duplicate_count: int,
        stale_count: int,
    ) -> dict:
        """Calculate the policy health score from finding counts.

        Rules:
            Start score  = 100
            Conflict     = -30 each
            Duplicate    = -10 each
            Stale        = -20 each
            Minimum      = 0
        """
        score = 100
        score -= conflict_count  * cls.CONFLICT_PENALTY
        score -= duplicate_count * cls.DUPLICATE_PENALTY
        score -= stale_count     * cls.STALE_PENALTY
        score = max(0, score)

        if score >= 85:
            status = "healthy"
        elif score >= 65:
            status = "warning"
        else:
            status = "critical"

        issues: list[str] = []
        if conflict_count:
            issues.append(f"{conflict_count} conflict{'s' if conflict_count > 1 else ''} detected (-{conflict_count * cls.CONFLICT_PENALTY} pts)")
        if duplicate_count:
            issues.append(f"{duplicate_count} duplicate{'s' if duplicate_count > 1 else ''} detected (-{duplicate_count * cls.DUPLICATE_PENALTY} pts)")
        if stale_count:
            issues.append(f"{stale_count} stale polic{'ies' if stale_count > 1 else 'y'} detected (-{stale_count * cls.STALE_PENALTY} pts)")

        summary = (
            "No issues detected – policy is in good standing."
            if not issues
            else "Health deductions: " + "; ".join(issues) + "."
        )

        return {
            "score":  score,
            "status": status,
            "summary": summary,
        }

    def evaluate(self, text: str, last_reviewed: str | None, db_session: Session | None = None) -> dict:
        is_duplicate = False
        similarity_score = 0.0
        match_type = "none"
        if db_session:
            from backend.app.models.policy import Policy
            # Query all existing policies
            other_policies = db_session.query(Policy).all()
            for op in other_policies:
                res = self.duplicate_detector.detect(text, op.raw_text)
                if res["is_duplicate"] and res["similarity_score"] > similarity_score:
                    is_duplicate = True
                    similarity_score = res["similarity_score"]
                    match_type = res["type"]
            duplicate_result = {
                "is_duplicate": is_duplicate,
                "similarity_score": similarity_score,
                "type": match_type
            }
        else:
            duplicate_result = {"is_duplicate": False, "similarity_score": 0.0, "type": "none"}

        staleness_result = self.staleness_detector.detect(text, last_reviewed)
        return {
            "duplicate": duplicate_result,
            "staleness": staleness_result,
        }

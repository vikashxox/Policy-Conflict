from sqlalchemy.orm import Session

from backend.app.models.policy import Policy
from backend.app.models.obligation import Obligation
from backend.app.models.finding import Finding
from backend.app.models.report import Report
from backend.app.models.activity_log import ActivityLog


class PolicyRepositoryDB:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_policy(self, data: dict) -> Policy:
        policy = Policy(**data)
        self.session.add(policy)
        self.session.commit()
        self.session.refresh(policy)
        return policy

    def list_policies(self) -> list[Policy]:
        return self.session.query(Policy).order_by(Policy.id.desc()).all()

    def get_policy(self, policy_id: int) -> Policy | None:
        return self.session.query(Policy).filter(Policy.id == policy_id).first()

    def create_obligation(self, policy_id: int, obligation: dict) -> Obligation:
        item = Obligation(policy_id=policy_id, **obligation)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def create_finding(self, finding: dict) -> Finding:
        item = Finding(**finding)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def create_report(self, report: dict) -> Report:
        item = Report(**report)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def create_activity(self, activity: dict) -> ActivityLog:
        item = ActivityLog(**activity)
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

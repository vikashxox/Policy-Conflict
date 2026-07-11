from backend.app.repositories.policy_repository import PolicyRepository
from backend.app.schemas.policy import DashboardResponse, FindingOut, PolicyOut


class PolicyService:
    def __init__(self, repository: PolicyRepository | None = None) -> None:
        self.repository = repository or PolicyRepository()

    def get_dashboard(self) -> DashboardResponse:
        data = self.repository.get_dashboard_data()
        return DashboardResponse(**data)

    def get_policy(self, policy_id: str) -> PolicyOut | None:
        return self.repository.get_policy(policy_id)

    def list_policies(self) -> list[PolicyOut]:
        return self.repository.list_policies()

    def list_findings(self) -> list[FindingOut]:
        return self.repository.list_findings()

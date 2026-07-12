import csv
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.policy import Policy
from backend.app.models.obligation import Obligation
from backend.app.models.finding import Finding
from backend.app.models.activity_log import ActivityLog
from backend.app.detectors.obligation_detector import ObligationDetector
from backend.app.detectors.conflict_detector import ConflictDetector
from backend.app.detectors.duplicate_detector import DuplicateDetector
from backend.app.detectors.staleness_detector import StalenessDetector
from backend.app.services.ai_insights_service import AiInsightsService
from backend.app.services.policy_health_service import PolicyHealthService

logger = logging.getLogger("policy-conflict")


class DatasetLoaderService:
    def __init__(self, dataset_path: str | None = None) -> None:
        self.dataset_path = Path(dataset_path or settings.grc_dataset_path)

    def load_dataset(self) -> list[dict[str, Any]]:
        csv_path = self.dataset_path / "policy_metadata.csv"
        policies_dir = self.dataset_path / "policies"

        if not csv_path.exists():
            logger.error(f"Metadata CSV not found at: {csv_path}")
            return []

        unified_policies = []
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_name = row.get("file") or ""
                    if not file_name:
                        continue
                    md_path = policies_dir / file_name
                    if not md_path.exists():
                        logger.warning(f"Markdown file {file_name} not found at {md_path}")
                        continue

                    with open(md_path, mode="r", encoding="utf-8") as md_file:
                        markdown_content = md_file.read()

                    unified_policies.append({
                        "file_name": file_name,
                        "title": row.get("title") or "",
                        "author": row.get("author") or "",
                        "department": row.get("department") or "",
                        "version": row.get("version") or "",
                        "status": row.get("status") or "active",
                        "last_reviewed": row.get("last_reviewed") or "",
                        "markdown_content": markdown_content
                    })
        except Exception as e:
            logger.exception(f"Error loading dataset: {e}")

        return unified_policies

    def _get_category(self, title: str) -> str:
        t = title.lower()
        if "password" in t or "access" in t or "provisioning" in t:
            return "Access Control"
        if "network" in t or "vpn" in t or "firewall" in t:
            return "Network"
        if "cloud" in t:
            return "Cloud"
        if "data" in t or "retention" in t or "classification" in t:
            return "Data Security"
        if "encryption" in t:
            return "Encryption"
        if "backup" in t or "recovery" in t:
            return "Backup"
        if "compliance" in t or "incident" in t:
            return "Compliance"
        if "vendor" in t or "third-party" in t:
            return "Third-Party Management"
        return "General"

    def seed_database(self, session: Session) -> None:
        """Seed GRC Hackathon dataset into the database and run detectors."""
        # 1. Check if policies table is already seeded
        if session.query(Policy).count() > 0:
            logger.info("Database already contains policies. Skipping dataset seeding.")
            return

        logger.info("Starting database seeding with GRC Hackathon dataset...")
        unified_policies = self.load_dataset()
        if not unified_policies:
            logger.warning("No dataset policies loaded. Seeding aborted.")
            return

        obligation_detector = ObligationDetector()
        conflict_detector = ConflictDetector()
        duplicate_detector = DuplicateDetector()
        staleness_detector = StalenessDetector()
        ai_insights_service = AiInsightsService()

        # 2. Add Policies
        db_policies: list[Policy] = []
        for p in unified_policies:
            title = p["title"]
            policy = Policy(
                external_id=p["file_name"],
                name=title,
                category=self._get_category(title),
                owner=p["author"],
                department=p["department"],
                version=p["version"],
                effective_date=p["last_reviewed"],
                last_reviewed=p["last_reviewed"],
                status=p["status"],
                summary=f"Automated policy for {title}",
                raw_text=p["markdown_content"],
                health=100,
                severity="healthy"
            )
            session.add(policy)
            db_policies.append(policy)
        
        session.commit()

        # Refresh to obtain database-assigned IDs
        for policy in db_policies:
            session.refresh(policy)

        # Keep track of obligations for conflict checking
        all_obligations_by_policy_id: dict[int, list[dict[str, Any]]] = {}

        # 3. Extract and save Obligations
        for policy in db_policies:
            extracted_obligations = obligation_detector.extract(policy.raw_text)
            all_obligations_by_policy_id[policy.id] = extracted_obligations

            for ob in extracted_obligations:
                obligation = Obligation(
                    policy_id=policy.id,
                    text=ob["text"],
                    strength=ob["strength"],
                    scope=ob["scope"],
                    category=ob["category"],
                    action=ob["action"]
                )
                session.add(obligation)
        
        session.commit()

        # 4. Detect and save Duplicates (Cross-checking every policy pair)
        for i, policy_a in enumerate(db_policies):
            for j, policy_b in enumerate(db_policies):
                if i >= j:
                    continue
                dup_result = duplicate_detector.detect(policy_a.raw_text, policy_b.raw_text)
                if dup_result["is_duplicate"]:
                    finding = Finding(
                        severity="warning" if dup_result["type"] == "near" else "critical",
                        finding_type="Duplicate Policy",
                        policy_a=policy_a.name,
                        policy_b=policy_b.name,
                        section="General",
                        confidence=int(dup_result["similarity_score"] * 100),
                        description=f"Policy '{policy_a.name}' is a duplicate of '{policy_b.name}' ({dup_result['type']} match).",
                        recommendation="Consolidate duplicate policies into a single master document.",
                        compliance="General Governance",
                        status="open",
                        category=policy_a.category
                    )
                    session.add(finding)

        # 5. Detect and save Conflicts (Cross-checking obligations)
        for i, policy_a in enumerate(db_policies):
            obs_a = all_obligations_by_policy_id[policy_a.id]
            for j, policy_b in enumerate(db_policies):
                if i >= j:
                    continue
                obs_b = all_obligations_by_policy_id[policy_b.id]
                conflicts = conflict_detector.detect(obs_a, obs_b)
                for conf in conflicts:
                    finding = Finding(
                        severity=conf["severity"],
                        finding_type="Direct Conflict",
                        policy_a=policy_a.name,
                        policy_b=policy_b.name,
                        section="General",
                        confidence=conf["confidence"],
                        description=conf["description"],
                        recommendation=conf["recommendation"],
                        compliance="Conflict Alignment",
                        status="open",
                        category=policy_a.category
                    )
                    session.add(finding)

        # 6. Detect and save Staleness
        for policy in db_policies:
            stale_result = staleness_detector.detect(policy.raw_text, policy.last_reviewed)
            if stale_result["is_stale"]:
                finding = Finding(
                    severity="warning",
                    finding_type="Stale Policy",
                    policy_a=policy.name,
                    policy_b="—",
                    section="General",
                    confidence=85,
                    description=f"Policy '{policy.name}' has been flagged as stale: {stale_result['reason']}",
                    recommendation="; ".join(stale_result["recommendations"]),
                    compliance="Governance Lifecycle",
                    status="open",
                    category=policy.category
                )
                session.add(finding)

        session.commit()

        # 7. Compute health and update Policy Health Score in DB
        # Retrieve all findings to calculate individual health scores
        all_findings = session.query(Finding).all()
        for policy in db_policies:
            # Count relevant findings for this policy
            p_findings = [
                f for f in all_findings
                if f.policy_a == policy.name or f.policy_b == policy.name
            ]
            conflict_count  = sum(1 for f in p_findings if f.finding_type == "Direct Conflict")
            duplicate_count = sum(1 for f in p_findings if f.finding_type == "Duplicate Policy")
            stale_count     = sum(1 for f in p_findings if f.finding_type == "Stale Policy")

            result = PolicyHealthService.calculate_score(
                conflict_count=conflict_count,
                duplicate_count=duplicate_count,
                stale_count=stale_count,
            )
            policy.health   = result["score"]
            policy.severity = result["status"]

        session.commit()

        # 8. Record Activity logs
        session.add(
            ActivityLog(
                actor="System Loader",
                action="seeded",
                target=f"{len(db_policies)} policies",
                severity="healthy"
            )
        )
        session.commit()
        logger.info(f"Database seeded successfully with {len(db_policies)} policies.")

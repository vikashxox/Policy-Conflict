from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from backend.app.parser.extractor import PolicyParser


class UploadService:
    def __init__(self, parser: PolicyParser | None = None) -> None:
        self.parser = parser or PolicyParser()
        self.upload_dir = Path("backend/app/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def process_upload(self, filename: str, content: bytes) -> dict[str, Any]:
        """Parse, persist, detect, score, and log an uploaded policy file."""
        parsed = self.parser.parse(filename, content)

        # Persist file to disk
        destination = self.upload_dir / filename
        destination.write_bytes(content)

        # Persist to database and run detectors
        try:
            result = self._persist_and_detect(filename, parsed)
        except Exception as exc:
            result = {"db_status": f"parse-only (db error: {exc})"}

        return {
            "id":       f"U-{destination.stem.lower()}",
            "filename": filename,
            "status":   "uploaded",
            "parsed":   parsed,
            **result,
        }

    def _persist_and_detect(self, filename: str, parsed: dict[str, Any]) -> dict[str, Any]:
        from backend.app.database.session import SessionLocal
        from backend.app.models.policy import Policy
        from backend.app.models.obligation import Obligation
        from backend.app.models.finding import Finding
        from backend.app.models.activity_log import ActivityLog
        from backend.app.detectors.obligation_detector import ObligationDetector
        from backend.app.detectors.conflict_detector import ConflictDetector
        from backend.app.detectors.duplicate_detector import DuplicateDetector
        from backend.app.detectors.staleness_detector import StalenessDetector
        from backend.app.services.policy_health_service import PolicyHealthService

        session = SessionLocal()
        try:
            # ── 1. Upsert Policy ──────────────────────────────────────
            external_id = filename
            existing = session.query(Policy).filter(Policy.external_id == external_id).first()
            raw_text = parsed.get("raw_text", "")

            if existing:
                policy = existing
                policy.name         = parsed.get("policy_name", filename)
                policy.raw_text     = raw_text
                policy.last_reviewed = parsed.get("last_reviewed") or ""
            else:
                policy = Policy(
                    external_id  = external_id,
                    name         = parsed.get("policy_name", filename),
                    category     = self._guess_category(parsed),
                    owner        = parsed.get("owner", "Unknown"),
                    department   = parsed.get("department", "Security"),
                    version      = parsed.get("version", "v1.0"),
                    effective_date = parsed.get("effective_date") or "",
                    last_reviewed  = parsed.get("last_reviewed") or "",
                    status       = parsed.get("status", "active"),
                    raw_text     = raw_text,
                    summary      = f"Uploaded policy: {parsed.get('policy_name', filename)}",
                    health       = 100,
                    severity     = "healthy",
                )
                session.add(policy)
            session.flush()

            # ── 2. Extract & store obligations ────────────────────────
            ob_detector = ObligationDetector()
            new_obligations = ob_detector.extract(raw_text)
            # Remove old obligations for this policy
            session.query(Obligation).filter(Obligation.policy_id == policy.id).delete()
            ob_objects: list[Obligation] = []
            for ob in new_obligations:
                item = Obligation(
                    policy_id = policy.id,
                    text      = ob["text"],
                    strength  = ob["strength"],
                    scope     = ob.get("scope", "general"),
                    category  = ob.get("category", "Other"),
                    action    = ob.get("action", ob["text"]),
                )
                session.add(item)
                ob_objects.append(item)
            session.flush()

            # ── 3. Remove old findings for this policy ────────────────
            session.query(Finding).filter(
                (Finding.policy_a == policy.name) | (Finding.policy_b == policy.name)
            ).delete()
            session.flush()

            conflict_count = 0
            duplicate_count = 0
            stale_count = 0

            # ── 4. Cross-conflict with every other policy ─────────────
            con_detector = ConflictDetector()
            other_policies = session.query(Policy).filter(Policy.id != policy.id).all()
            for other in other_policies:
                other_obs = [
                    {"text": o.text, "strength": o.strength, "category": o.category, "scope": o.scope}
                    for o in session.query(Obligation).filter(Obligation.policy_id == other.id).all()
                ]
                my_obs = [
                    {"text": o.text, "strength": o.strength, "category": o.category, "scope": o.scope}
                    for o in ob_objects
                ]
                conflicts = con_detector.detect(my_obs, other_obs)
                for conf in conflicts:
                    session.add(Finding(
                        severity       = conf["severity"],
                        finding_type   = "Direct Conflict",
                        policy_a       = policy.name,
                        policy_b       = other.name,
                        section        = "General",
                        confidence     = conf["confidence"],
                        description    = conf["description"],
                        recommendation = conf["recommendation"],
                        compliance     = "Conflict Alignment",
                        status         = "open",
                        category       = policy.category,
                    ))
                    conflict_count += 1

            # ── 5. Duplicate check ────────────────────────────────────
            dup_detector = DuplicateDetector()
            for other in other_policies:
                if not other.raw_text:
                    continue
                dup = dup_detector.detect(raw_text, other.raw_text)
                if dup["is_duplicate"]:
                    session.add(Finding(
                        severity       = "warning",
                        finding_type   = "Duplicate Policy",
                        policy_a       = policy.name,
                        policy_b       = other.name,
                        section        = "General",
                        confidence     = int(dup["similarity_percentage"]),
                        description    = (
                            f"'{policy.name}' is a {dup['type']} duplicate of '{other.name}' "
                            f"({dup['similarity_percentage']}% similarity)."
                        ),
                        recommendation = "Merge or decommission one of the duplicate policies.",
                        compliance     = "Governance",
                        status         = "open",
                        category       = policy.category,
                    ))
                    duplicate_count += 1

            # ── 6. Staleness ──────────────────────────────────────────
            stale_detector = StalenessDetector()
            stale = stale_detector.detect(raw_text, policy.last_reviewed)
            if stale["is_stale"]:
                session.add(Finding(
                    severity       = "warning",
                    finding_type   = "Stale Policy",
                    policy_a       = policy.name,
                    policy_b       = "—",
                    section        = "General",
                    confidence     = 85,
                    description    = f"Policy '{policy.name}' is stale: {stale['reason']}",
                    recommendation = "; ".join(stale["recommendations"]),
                    compliance     = "Governance Lifecycle",
                    status         = "open",
                    category       = policy.category,
                ))
                stale_count += 1

            # ── 7. Compute & persist health score ─────────────────────
            health = PolicyHealthService.calculate_score(
                conflict_count  = conflict_count,
                duplicate_count = duplicate_count,
                stale_count     = stale_count,
            )
            policy.health   = health["score"]
            policy.severity = health["status"]
            policy.summary  = health["summary"]

            # ── 8. Activity log ───────────────────────────────────────
            session.add(ActivityLog(
                actor    = "Upload Service",
                action   = "uploaded",
                target   = filename,
                severity = health["status"],
            ))

            session.commit()

            return {
                "db_status":      "persisted",
                "policy_id":      policy.external_id,
                "obligations":    len(ob_objects),
                "conflicts":      conflict_count,
                "duplicates":     duplicate_count,
                "stale":          stale_count,
                "health_score":   health["score"],
                "health_status":  health["status"],
                "health_summary": health["summary"],
            }
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _guess_category(self, parsed: dict[str, Any]) -> str:
        text = (parsed.get("policy_name", "") + " " + parsed.get("raw_text", "")[:500]).lower()
        mapping = [
            (["password", "credential", "passcode"],              "Password"),
            (["authentication", "mfa", "sso", "identity"],        "Authentication"),
            (["cloud", "aws", "azure", "gcp"],                    "Cloud"),
            (["encryption", "tls", "aes", "ssl"],                 "Encryption"),
            (["logging", "audit trail"],                           "Logging"),
            (["firewall", "waf"],                                   "Firewall"),
            (["vpn", "remote access"],                             "VPN"),
            (["network", "router", "dns"],                         "Network"),
            (["backup", "recovery", "restore"],                    "Backup"),
            (["retention", "archive"],                             "Data Retention"),
            (["compliance", "gdpr", "hipaa", "sox", "pci"],       "Compliance"),
            (["access control", "access management", "rbac"],     "Access Control"),
        ]
        for keywords, label in mapping:
            if any(kw in text for kw in keywords):
                return label
        return "General"

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class PolicyParser:
    def parse(self, filename: str, content: bytes) -> dict[str, Any]:
        text = self._decode_content(content)
        metadata = self._extract_metadata(text)
        policy_name = (
            metadata.get("policy_name")
            or metadata.get("title")
            or Path(filename).stem.replace("-", " ").replace("_", " ").title()
        )
        version = metadata.get("version") or self._extract_field(text, "Version") or "v1.0"
        department = metadata.get("department") or self._extract_field(text, "Department") or "Security"
        owner = metadata.get("owner") or self._extract_field(text, "Owner") or "Unknown"
        effective_date = metadata.get("effective_date") or self._extract_field(text, "Effective Date")
        last_reviewed = metadata.get("last_reviewed") or self._extract_field(text, "Last Reviewed")
        sections = max(1, len(re.findall(r"^#{1,6}\s+", text, flags=re.MULTILINE)))
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        return {
            "policy_name": policy_name,
            "policyName": policy_name,
            "version": version,
            "department": department,
            "owner": owner,
            "effective_date": effective_date,
            "effectiveDate": effective_date,
            "last_reviewed": last_reviewed,
            "lastReviewed": last_reviewed,
            "sections": sections,
            "paragraphs": paragraphs,
            "metadata": metadata,
            "raw_text": text[:4000],
            "rawText": text[:4000],
        }

    def _decode_content(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="ignore")

    def _extract_metadata(self, text: str) -> dict[str, str]:
        metadata: dict[str, str] = {}
        title = self._extract_field(text, "Title") or self._extract_field(text, "Policy Name")
        if title:
            metadata["title"] = title
            metadata["policy_name"] = title
        version = self._extract_field(text, "Version")
        if version:
            metadata["version"] = version
        department = self._extract_field(text, "Department")
        if department:
            metadata["department"] = department
        owner = self._extract_field(text, "Owner")
        if owner:
            metadata["owner"] = owner
        effective_date = self._extract_field(text, "Effective Date")
        if effective_date:
            metadata["effective_date"] = effective_date
        last_reviewed = self._extract_field(text, "Last Reviewed")
        if last_reviewed:
            metadata["last_reviewed"] = last_reviewed
        return metadata

    def _extract_field(self, text: str, field_name: str) -> str | None:
        patterns = [
            rf"{re.escape(field_name)}\s*[:\-]\s*(.+)",
            rf"^#{1,6}\s*{re.escape(field_name)}\s*[:\-]\s*(.+)$",
            rf"^\*\*{re.escape(field_name)}\*\*\s*[:\-]\s*(.+)$",
        ]
        for pattern_text in patterns:
            match = re.search(pattern_text, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        return None

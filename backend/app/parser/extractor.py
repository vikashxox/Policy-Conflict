from __future__ import annotations

import re
from pathlib import Path
from typing import BinaryIO


class PolicyParser:
    def parse(self, filename: str, content: bytes) -> dict:
        text = self._decode_content(content)
        policy_name = self._extract_field(text, "Policy Name") or Path(filename).stem.replace("-", " ").title()
        version = self._extract_field(text, "Version") or "v1.0"
        department = self._extract_field(text, "Department") or "Security"
        owner = self._extract_field(text, "Owner") or "Unknown"
        effective_date = self._extract_field(text, "Effective Date")
        last_reviewed = self._extract_field(text, "Last Reviewed")
        sections = max(1, len(re.findall(r"^#{1,6}\s+", text, flags=re.MULTILINE)))

        return {
            "policy_name": policy_name,
            "version": version,
            "department": department,
            "owner": owner,
            "effective_date": effective_date,
            "last_reviewed": last_reviewed,
            "sections": sections,
            "raw_text": text[:4000],
        }

    def _decode_content(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="ignore")

    def _extract_field(self, text: str, field_name: str) -> str | None:
        pattern = re.compile(rf"{re.escape(field_name)}\s*[:\-]\s*(.+)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
        return None

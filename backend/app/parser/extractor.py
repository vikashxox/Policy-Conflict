from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any


class PolicyParser:
    def parse(self, filename: str, content: bytes) -> dict[str, Any]:
        text = self._decode_content(content)
        metadata = self._extract_metadata(text)

        # Try to find metadata from policy_metadata.csv if available
        csv_metadata = {}
        try:
            from backend.app.core.config import settings
            csv_path = Path(settings.grc_dataset_path) / "policy_metadata.csv"
            if csv_path.exists():
                with open(csv_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row_file = row.get("file") or ""
                        if row_file == filename or Path(row_file).name == Path(filename).name:
                            csv_metadata = row
                            break
        except Exception:
            pass

        # Extract Policy Title
        policy_name = (
            csv_metadata.get("title")
            or metadata.get("policy_name")
            or metadata.get("title")
            or self._extract_field(text, "Title")
            or self._extract_field(text, "Policy Name")
            or Path(filename).stem.replace("-", " ").replace("_", " ").title()
        )

        owner = csv_metadata.get("author") or metadata.get("owner") or self._extract_field(text, "Owner") or "Unknown"
        department = csv_metadata.get("department") or metadata.get("department") or self._extract_field(text, "Department") or "Security"
        version = csv_metadata.get("version") or metadata.get("version") or self._extract_field(text, "Version") or "v1.0"
        status = csv_metadata.get("status") or metadata.get("status") or self._extract_field(text, "Status") or "active"
        last_reviewed = csv_metadata.get("last_reviewed") or metadata.get("last_reviewed") or self._extract_field(text, "Last Reviewed") or ""

        # Split into sections
        sections_list = []
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))

        if not matches:
            sections_list.append({"title": "General", "content": text})
        else:
            for i in range(len(matches)):
                match = matches[i]
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                sections_list.append({
                    "title": match.group(2).strip(),
                    "content": text[start:end].strip()
                })

        # Split into paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

        # Split into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

        # Extract Obligation sentences
        obligation_keywords = {"must", "shall", "required", "require", "requires", "mandatory", "obligated", "must not", "shall not", "prohibited", "recommended", "should"}
        obligation_sentences = []
        for s in sentences:
            lowered_s = s.lower()
            if any(keyword in lowered_s for keyword in obligation_keywords):
                obligation_sentences.append(s)

        merged_metadata = {
            **metadata,
            **csv_metadata
        }

        return {
            "policy_name": policy_name,
            "policyName": policy_name,
            "version": version,
            "department": department,
            "owner": owner,
            "effective_date": last_reviewed,
            "effectiveDate": last_reviewed,
            "last_reviewed": last_reviewed,
            "lastReviewed": last_reviewed,
            "status": status,
            "sections": len(sections_list),  # Keep as integer for schema validation
            "sections_list": sections_list,  # Extended section detail list
            "paragraphs": paragraphs,
            "sentences": sentences,
            "obligation_sentences": obligation_sentences,
            "metadata": merged_metadata,
            "raw_text": text,
            "rawText": text,
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

from __future__ import annotations

import json
from typing import Any


class ReportService:
    def generate_report(self, title: str, payload: dict[str, Any], report_format: str = "json") -> dict[str, Any]:
        content = json.dumps({"title": title, **payload}, indent=2)
        return {
            "title": title,
            "format": report_format,
            "content": content,
            "download_url": f"/reports/{title.lower().replace(' ', '-')}.{report_format}",
        }

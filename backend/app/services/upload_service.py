from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from backend.app.parser.extractor import PolicyParser


class UploadService:
    def __init__(self, parser: PolicyParser | None = None) -> None:
        self.parser = parser or PolicyParser()
        self.upload_dir = Path("backend/app/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def process_upload(self, filename: str, content: bytes) -> dict:
        parsed = self.parser.parse(filename, content)
        destination = self.upload_dir / filename
        destination.write_bytes(content)
        return {
            "id": f"U-{destination.stem.lower()}",
            "filename": filename,
            "status": "uploaded",
            "parsed": parsed,
        }

from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerateScriptCommand:
    user_id: str
    topic_code: str
    tone: str
    title: Optional[str] = None
    notes: Optional[str] = None
    reference_image_bytes: Optional[bytes] = None
    reference_image_mime: Optional[str] = None
    reference_image_filename: Optional[str] = None


@dataclass
class GenerateScriptResponse:
    script: str
    draft_id: str
    script_version_id: str

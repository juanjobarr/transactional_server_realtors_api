from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ScriptVersion:
    id: Optional[str]
    draft_id: str
    version_number: int
    script_text: str
    structured_script: dict[str, Any] = field(default_factory=dict)
    estimated_read_time_seconds: int = 0
    is_approved: bool = False
    approved_by_user_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

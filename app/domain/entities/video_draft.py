from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class VideoDraft:
    id: Optional[str]
    user_id: str
    topic_id: str
    title: str
    tone: str
    pacing: str
    status: str
    current_step: str
    subject: Optional[str] = None
    property_address: Optional[str] = None
    description: Optional[str] = None
    bullet_points: list[Any] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

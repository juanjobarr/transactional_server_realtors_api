from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class WebhookEvent:
    id: Optional[str]
    source: str
    external_event_id: str
    event_type: str
    payload: dict[str, Any]
    status: str = "received"
    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

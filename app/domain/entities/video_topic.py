from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoTopic:
    id: str
    code: str
    label: str
    description: str
    icon: str
    active: bool
    created_at: datetime

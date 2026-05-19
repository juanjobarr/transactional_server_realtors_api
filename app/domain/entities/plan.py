from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Plan:
    id: str
    name: str
    monthly_video_limit: int
    monthly_scene_limit: int
    price: Decimal
    currency: str
    active: bool
    created_at: datetime
    updated_at: datetime

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class SubscriptionResponse:
    id: str
    plan_id: str
    plan_name: str
    billing_start: date
    billing_end: date
    status: str
    videos_used: int
    scenes_used: int
    videos_remaining: int
    monthly_video_limit: int
    monthly_scene_limit: int
    updated_at: datetime

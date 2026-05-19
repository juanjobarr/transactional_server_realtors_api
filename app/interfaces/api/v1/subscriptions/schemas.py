from datetime import date, datetime

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
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

    model_config = {"from_attributes": True}

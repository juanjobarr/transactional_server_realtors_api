from dataclasses import dataclass
from datetime import date, datetime

from app.domain.value_objects.subscription_status import SubscriptionStatus


@dataclass
class Subscription:
    id: str
    user_id: str
    plan_id: str
    billing_start: date
    billing_end: date
    status: SubscriptionStatus
    videos_used: int
    scenes_used: int
    videos_remaining: int
    created_at: datetime
    updated_at: datetime

    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

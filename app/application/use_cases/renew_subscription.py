import calendar
from datetime import date, datetime, timezone

from app.domain.ports.plan_repository import PlanRepositoryPort
from app.domain.ports.subscription_repository import SubscriptionRepositoryPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.value_objects.subscription_status import SubscriptionStatus
from app.domain.value_objects.user_status import UserStatus


def _current_billing_period() -> tuple[date, date]:
    today = date.today()
    start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = today.replace(day=last_day)
    return start, end


class RenewSubscription:
    def __init__(
        self,
        subscription_repo: SubscriptionRepositoryPort,
        user_repo: UserRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def execute(self, user_id: str) -> None:
        subscription = self.subscription_repo.find_latest_by_user_id(user_id)
        if not subscription:
            raise ValueError("No subscription found for this user")

        plan = self.plan_repo.find_by_id(subscription.plan_id)
        billing_start, billing_end = _current_billing_period()
        now = datetime.now(timezone.utc)

        subscription.billing_start = billing_start
        subscription.billing_end = billing_end
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.videos_used = 0
        subscription.scenes_used = 0
        subscription.videos_remaining = plan.monthly_video_limit if plan else subscription.videos_remaining
        subscription.updated_at = now
        self.subscription_repo.update(subscription)

        user = self.user_repo.find_by_id(user_id)
        if user:
            user.status = UserStatus.ACTIVE
            user.updated_at = now
            self.user_repo.update(user)

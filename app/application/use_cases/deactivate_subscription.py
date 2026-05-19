from datetime import datetime, timezone

from app.domain.ports.subscription_repository import SubscriptionRepositoryPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.value_objects.subscription_status import SubscriptionStatus
from app.domain.value_objects.user_status import UserStatus


class DeactivateSubscription:
    def __init__(
        self,
        subscription_repo: SubscriptionRepositoryPort,
        user_repo: UserRepositoryPort,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo

    def execute(self, user_id: str) -> None:
        subscription = self.subscription_repo.find_active_by_user_id(user_id)
        if not subscription:
            raise ValueError("No active subscription found for this user")

        subscription.status = SubscriptionStatus.INACTIVE
        subscription.updated_at = datetime.now(timezone.utc)
        self.subscription_repo.update(subscription)

        user = self.user_repo.find_by_id(user_id)
        if user:
            user.status = UserStatus.INACTIVE
            user.updated_at = datetime.now(timezone.utc)
            self.user_repo.update(user)

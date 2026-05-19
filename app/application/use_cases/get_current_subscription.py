from app.application.dto.subscription_dto import SubscriptionResponse
from app.domain.ports.plan_repository import PlanRepositoryPort
from app.domain.ports.subscription_repository import SubscriptionRepositoryPort


class GetCurrentSubscription:
    def __init__(
        self,
        subscription_repo: SubscriptionRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo

    def execute(self, user_id: str) -> SubscriptionResponse:
        subscription = self.subscription_repo.find_latest_by_user_id(user_id)
        if not subscription:
            raise ValueError("No subscription found for this user")

        plan = self.plan_repo.find_by_id(subscription.plan_id)
        plan_name = plan.name if plan else "Unknown"
        monthly_video_limit = plan.monthly_video_limit if plan else 0
        monthly_scene_limit = plan.monthly_scene_limit if plan else 0

        return SubscriptionResponse(
            id=subscription.id,
            plan_id=subscription.plan_id,
            plan_name=plan_name,
            billing_start=subscription.billing_start,
            billing_end=subscription.billing_end,
            status=subscription.status.value,
            videos_used=subscription.videos_used,
            scenes_used=subscription.scenes_used,
            videos_remaining=subscription.videos_remaining,
            monthly_video_limit=monthly_video_limit,
            monthly_scene_limit=monthly_scene_limit,
            updated_at=subscription.updated_at,
        )

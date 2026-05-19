from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.subscription import Subscription
from app.domain.ports.subscription_repository import SubscriptionRepositoryPort
from app.domain.value_objects.subscription_status import SubscriptionStatus
from app.infrastructure.db.models.subscription_model import SubscriptionModel


class SQLAlchemySubscriptionRepository(SubscriptionRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_active_by_user_id(self, user_id: str) -> Optional[Subscription]:
        row = (
            self.db.query(SubscriptionModel)
            .filter(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.status == SubscriptionStatus.ACTIVE.value,
            )
            .first()
        )
        return self._to_entity(row) if row else None

    def find_latest_by_user_id(self, user_id: str) -> Optional[Subscription]:
        row = (
            self.db.query(SubscriptionModel)
            .filter(SubscriptionModel.user_id == user_id)
            .order_by(SubscriptionModel.created_at.desc())
            .first()
        )
        return self._to_entity(row) if row else None

    def save(self, subscription: Subscription) -> Subscription:
        model = SubscriptionModel(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            billing_start=subscription.billing_start,
            billing_end=subscription.billing_end,
            status=subscription.status.value,
            videos_used=subscription.videos_used,
            scenes_used=subscription.scenes_used,
            videos_remaining=subscription.videos_remaining,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, subscription: Subscription) -> Subscription:
        self.db.query(SubscriptionModel).filter(
            SubscriptionModel.id == subscription.id
        ).update(
            {
                "billing_start": subscription.billing_start,
                "billing_end": subscription.billing_end,
                "status": subscription.status.value,
                "videos_used": subscription.videos_used,
                "scenes_used": subscription.scenes_used,
                "videos_remaining": subscription.videos_remaining,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        self.db.commit()
        return subscription

    @staticmethod
    def _to_entity(row: SubscriptionModel) -> Subscription:
        return Subscription(
            id=str(row.id),
            user_id=str(row.user_id),
            plan_id=str(row.plan_id),
            billing_start=row.billing_start,
            billing_end=row.billing_end,
            status=SubscriptionStatus(row.status),
            videos_used=row.videos_used,
            scenes_used=row.scenes_used,
            videos_remaining=row.videos_remaining,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.use_cases.deactivate_subscription import DeactivateSubscription
from app.application.use_cases.get_current_subscription import GetCurrentSubscription
from app.application.use_cases.renew_subscription import RenewSubscription
from app.config import settings
from app.infrastructure.db.repositories.plan_repository import SQLAlchemyPlanRepository
from app.infrastructure.db.repositories.subscription_repository import (
    SQLAlchemySubscriptionRepository,
)
from app.infrastructure.db.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.db.session import get_db
from app.interfaces.api.dependencies.auth import get_current_user_id
from app.interfaces.api.v1.subscriptions.schemas import SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    use_case = GetCurrentSubscription(
        SQLAlchemySubscriptionRepository(db),
        SQLAlchemyPlanRepository(db),
    )
    try:
        result = use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return SubscriptionResponse(
        id=result.id,
        plan_id=result.plan_id,
        plan_name=result.plan_name,
        billing_start=result.billing_start,
        billing_end=result.billing_end,
        status=result.status,
        videos_used=result.videos_used,
        scenes_used=result.scenes_used,
        videos_remaining=result.videos_remaining,
        monthly_video_limit=result.monthly_video_limit,
        monthly_scene_limit=result.monthly_scene_limit,
        updated_at=result.updated_at,
    )


def _require_admin_key(x_admin_key: str = Header(...)) -> None:
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key")


@router.patch("/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
def deactivate(
    user_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(_require_admin_key),
):
    use_case = DeactivateSubscription(
        SQLAlchemySubscriptionRepository(db),
        SQLAlchemyUserRepository(db),
    )
    try:
        use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_id}/renew", status_code=status.HTTP_204_NO_CONTENT)
def renew(
    user_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(_require_admin_key),
):
    use_case = RenewSubscription(
        SQLAlchemySubscriptionRepository(db),
        SQLAlchemyUserRepository(db),
        SQLAlchemyPlanRepository(db),
    )
    try:
        use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

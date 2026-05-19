import calendar
import uuid
from datetime import date, datetime, timezone

from app.application.dto.auth_dto import RegisterUserCommand, TokensResponse
from app.domain.entities.subscription import Subscription
from app.domain.entities.user import User
from app.domain.ports.plan_repository import PlanRepositoryPort
from app.domain.ports.subscription_repository import SubscriptionRepositoryPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.password_service import hash_password
from app.domain.services.token_service import TokenService
from app.domain.value_objects.subscription_status import SubscriptionStatus
from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.user_status import UserStatus

_DEFAULT_PLAN_ID = "2c2c9a95-4eeb-4c3a-8176-210cec7af852"


def _current_billing_period() -> tuple[date, date]:
    today = date.today()
    start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = today.replace(day=last_day)
    return start, end


class RegisterUser:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        token_service: TokenService,
        subscription_repo: SubscriptionRepositoryPort,
        plan_repo: PlanRepositoryPort,
    ) -> None:
        self.user_repo = user_repo
        self.token_service = token_service
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo

    def execute(self, command: RegisterUserCommand) -> TokensResponse:
        if self.user_repo.exists_by_email(command.email.lower()):
            raise ValueError("Email already registered")

        plan = self.plan_repo.find_by_id(_DEFAULT_PLAN_ID)
        if not plan:
            raise ValueError("Default plan not found")

        now = datetime.now(timezone.utc)
        user = User(
            id=str(uuid.uuid4()),
            full_name=command.full_name.strip(),
            email=command.email.lower(),
            password_hash=hash_password(command.password),
            avatar_initials=User.build_initials(command.full_name.strip()),
            role=UserRole.REALTOR,
            status=UserStatus.ACTIVE,
            is_email_verified=False,
            last_login_at=None,
            created_at=now,
            updated_at=now,
        )

        saved = self.user_repo.save(user)

        billing_start, billing_end = _current_billing_period()
        subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=saved.id,
            plan_id=plan.id,
            billing_start=billing_start,
            billing_end=billing_end,
            status=SubscriptionStatus.ACTIVE,
            videos_used=0,
            scenes_used=0,
            videos_remaining=plan.monthly_video_limit,
            created_at=now,
            updated_at=now,
        )
        self.subscription_repo.save(subscription)

        return TokensResponse(
            access_token=self.token_service.create_access_token(saved.id, saved.role.value),
            refresh_token=self.token_service.create_refresh_token(saved.id),
        )

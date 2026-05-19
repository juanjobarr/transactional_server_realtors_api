from app.application.dto.auth_dto import UserResponse
from app.domain.ports.user_repository import UserRepositoryPort


class GetCurrentUser:
    def __init__(self, user_repo: UserRepositoryPort) -> None:
        self.user_repo = user_repo

    def execute(self, user_id: str) -> UserResponse:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return UserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            avatar_initials=user.avatar_initials,
            role=user.role.value,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )

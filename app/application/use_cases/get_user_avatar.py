from app.application.dto.user_avatar_dto import GetUserAvatarResult
from app.domain.ports.user_avatar_repository import UserAvatarRepositoryPort


class GetUserAvatar:
    def __init__(self, avatar_repo: UserAvatarRepositoryPort) -> None:
        self.avatar_repo = avatar_repo

    def execute(self, user_id: str) -> GetUserAvatarResult:
        avatar = self.avatar_repo.find_by_user_id(user_id)
        if not avatar:
            raise LookupError("Avatar not found")

        return GetUserAvatarResult(
            status=avatar.status.value,
            avatar_url=avatar.avatar_url,
            additional_instructions=avatar.additional_instructions,
            reference_image_urls=avatar.reference_image_urls,
            error_message=avatar.error_message,
            updated_at=avatar.updated_at,
        )

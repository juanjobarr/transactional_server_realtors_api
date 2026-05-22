from app.application.dto.user_avatar_dto import (
    GenerateAvatarCommand,
    GenerateAvatarResult,
)
from app.config import settings
from app.domain.entities.user_avatar import UserAvatar
from app.domain.ports.avatar_generator import AvatarGeneratorPort
from app.domain.ports.image_storage import ImageStoragePort
from app.domain.ports.user_avatar_repository import UserAvatarRepositoryPort
from app.domain.value_objects.avatar_status import AvatarStatus


class GenerateAvatar:
    def __init__(
        self,
        avatar_repo: UserAvatarRepositoryPort,
        image_storage: ImageStoragePort,
        generator: AvatarGeneratorPort,
    ) -> None:
        self.avatar_repo = avatar_repo
        self.image_storage = image_storage
        self.generator = generator

    def execute(self, command: GenerateAvatarCommand) -> GenerateAvatarResult:
        references_prefix = f"{command.user_id}_referencias"
        avatar_prefix = f"{command.user_id}_avatar"
        container = settings.AZURE_STORAGE_AVATAR_CONTAINER_NAME

        existing = self.avatar_repo.find_by_user_id(command.user_id)
        if existing:
            self.image_storage.delete_prefix(references_prefix, container=container)
            self.image_storage.delete_prefix(avatar_prefix, container=container)

        uploaded_urls: list[str] = []
        try:
            for image in command.images:
                url = self.image_storage.upload(
                    content=image.content,
                    content_type=image.content_type,
                    filename_hint=image.filename,
                    prefix=references_prefix,
                    container=container,
                )
                uploaded_urls.append(url)
        except Exception:
            self.image_storage.delete_prefix(references_prefix, container=container)
            raise

        callback_url = (
            f"{settings.AVATAR_PUBLIC_CALLBACK_BASE_URL.rstrip('/')}"
            f"/api/v1/avatars/webhook"
        )

        try:
            external_job_id = self.generator.submit(
                user_id=command.user_id,
                reference_urls=uploaded_urls,
                additional_instructions=command.additional_instructions,
                callback_url=callback_url,
            )
        except Exception:
            self.image_storage.delete_prefix(references_prefix, container=container)
            raise

        avatar = self.avatar_repo.upsert(
            UserAvatar(
                id=existing.id if existing else None,
                user_id=command.user_id,
                status=AvatarStatus.PENDING,
                additional_instructions=command.additional_instructions,
                reference_image_urls=uploaded_urls,
                avatar_url=None,
                external_job_id=external_job_id,
                error_message=None,
            )
        )

        return GenerateAvatarResult(
            avatar_id=avatar.id or "",
            status=avatar.status.value,
            external_job_id=external_job_id,
        )

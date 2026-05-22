from app.application.dto.user_avatar_dto import ProcessAvatarWebhookCommand
from app.config import settings
from app.domain.ports.image_storage import ImageStoragePort
from app.domain.ports.user_avatar_repository import UserAvatarRepositoryPort
from app.domain.ports.webhook_event_repository import WebhookEventRepositoryPort
from app.domain.value_objects.avatar_status import AvatarStatus


class ProcessAvatarWebhook:
    def __init__(
        self,
        avatar_repo: UserAvatarRepositoryPort,
        image_storage: ImageStoragePort,
        webhook_repo: WebhookEventRepositoryPort,
    ) -> None:
        self.avatar_repo = avatar_repo
        self.image_storage = image_storage
        self.webhook_repo = webhook_repo

    def execute(self, command: ProcessAvatarWebhookCommand) -> None:
        event = self.webhook_repo.record(
            source="avatar-service",
            external_event_id=command.external_job_id,
            event_type=f"avatar.{command.status}",
            payload={
                "external_job_id": command.external_job_id,
                "status": command.status,
                "avatar_url": command.avatar_url,
                "error_message": command.error_message,
            },
        )

        avatar = self.avatar_repo.find_by_external_job_id(command.external_job_id)
        if not avatar:
            self.webhook_repo.mark_processed(event.id or "", status="orphan")
            raise LookupError(
                f"No avatar found for external_job_id={command.external_job_id}"
            )

        if command.status == "ready":
            if not command.avatar_url:
                self.webhook_repo.mark_processed(event.id or "", status="invalid")
                raise ValueError("Webhook with status=ready must include avatar_url")

            final_url = self.image_storage.upload_from_url(
                command.avatar_url,
                prefix=f"{avatar.user_id}_avatar",
                filename_hint="avatar.png",
                container=settings.AZURE_STORAGE_AVATAR_CONTAINER_NAME,
            )
            self.avatar_repo.update_status(
                avatar.user_id,
                AvatarStatus.READY,
                avatar_url=final_url,
            )
        elif command.status == "failed":
            self.avatar_repo.update_status(
                avatar.user_id,
                AvatarStatus.FAILED,
                error_message=command.error_message or "Avatar generation failed",
            )
        else:
            self.webhook_repo.mark_processed(event.id or "", status="invalid")
            raise ValueError(f"Unknown webhook status: {command.status}")

        self.webhook_repo.mark_processed(event.id or "", status="processed")

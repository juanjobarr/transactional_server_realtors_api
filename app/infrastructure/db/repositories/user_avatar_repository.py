from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.user_avatar import UserAvatar
from app.domain.ports.user_avatar_repository import UserAvatarRepositoryPort
from app.domain.value_objects.avatar_status import AvatarStatus
from app.infrastructure.db.models.user_avatar_model import UserAvatarModel


class SQLAlchemyUserAvatarRepository(UserAvatarRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_user_id(self, user_id: str) -> Optional[UserAvatar]:
        row = (
            self.db.query(UserAvatarModel)
            .filter(UserAvatarModel.user_id == user_id)
            .first()
        )
        return self._to_entity(row) if row else None

    def find_by_external_job_id(self, external_job_id: str) -> Optional[UserAvatar]:
        row = (
            self.db.query(UserAvatarModel)
            .filter(UserAvatarModel.external_job_id == external_job_id)
            .first()
        )
        return self._to_entity(row) if row else None

    def upsert(self, avatar: UserAvatar) -> UserAvatar:
        existing = (
            self.db.query(UserAvatarModel)
            .filter(UserAvatarModel.user_id == avatar.user_id)
            .first()
        )
        if existing:
            existing.status = avatar.status.value
            existing.additional_instructions = avatar.additional_instructions
            existing.reference_image_urls = avatar.reference_image_urls
            existing.avatar_url = avatar.avatar_url
            existing.external_job_id = avatar.external_job_id
            existing.error_message = avatar.error_message
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return self._to_entity(existing)

        model = UserAvatarModel(
            user_id=avatar.user_id,
            status=avatar.status.value,
            additional_instructions=avatar.additional_instructions,
            reference_image_urls=avatar.reference_image_urls,
            avatar_url=avatar.avatar_url,
            external_job_id=avatar.external_job_id,
            error_message=avatar.error_message,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update_status(
        self,
        user_id: str,
        status: AvatarStatus,
        *,
        avatar_url: Optional[str] = None,
        external_job_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        updates: dict = {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc),
        }
        if avatar_url is not None:
            updates["avatar_url"] = avatar_url
        if external_job_id is not None:
            updates["external_job_id"] = external_job_id
        if error_message is not None:
            updates["error_message"] = error_message

        self.db.query(UserAvatarModel).filter(
            UserAvatarModel.user_id == user_id
        ).update(updates)
        self.db.commit()

    @staticmethod
    def _to_entity(row: UserAvatarModel) -> UserAvatar:
        return UserAvatar(
            id=str(row.id),
            user_id=str(row.user_id),
            status=AvatarStatus(row.status),
            additional_instructions=row.additional_instructions,
            reference_image_urls=list(row.reference_image_urls or []),
            avatar_url=row.avatar_url,
            external_job_id=row.external_job_id,
            error_message=row.error_message,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

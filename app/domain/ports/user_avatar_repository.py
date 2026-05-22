from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user_avatar import UserAvatar
from app.domain.value_objects.avatar_status import AvatarStatus


class UserAvatarRepositoryPort(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Optional[UserAvatar]: ...

    @abstractmethod
    def upsert(self, avatar: UserAvatar) -> UserAvatar: ...

    @abstractmethod
    def update_status(
        self,
        user_id: str,
        status: AvatarStatus,
        *,
        avatar_url: Optional[str] = None,
        external_job_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None: ...

    @abstractmethod
    def find_by_external_job_id(self, external_job_id: str) -> Optional[UserAvatar]: ...

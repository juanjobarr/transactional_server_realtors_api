from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.video_draft import VideoDraft


class VideoDraftRepositoryPort(ABC):
    @abstractmethod
    def create(self, draft: VideoDraft) -> VideoDraft: ...

    @abstractmethod
    def add_reference_image(
        self,
        draft_id: str,
        storage_url: str,
        role: str = "reference",
        sort_order: int = 0,
    ) -> None: ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> tuple[list[VideoDraft], int]: ...

    @abstractmethod
    def find_by_id_and_user(
        self,
        draft_id: str,
        user_id: str,
    ) -> Optional[VideoDraft]: ...

    @abstractmethod
    def update_status(self, draft_id: str, status: str) -> None: ...

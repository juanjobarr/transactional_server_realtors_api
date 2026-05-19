from abc import ABC, abstractmethod

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

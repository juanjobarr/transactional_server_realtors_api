from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.video import Video


class VideoRepositoryPort(ABC):
    @abstractmethod
    def create(self, video: Video) -> Video: ...

    @abstractmethod
    def find_by_draft_id(self, draft_id: str) -> Optional[Video]: ...

    @abstractmethod
    def find_by_id_and_user(self, video_id: str, user_id: str) -> Optional[Video]: ...

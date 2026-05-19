from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.video_topic import VideoTopic


class VideoTopicRepositoryPort(ABC):
    @abstractmethod
    def list_active(self) -> list[VideoTopic]: ...

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[VideoTopic]: ...

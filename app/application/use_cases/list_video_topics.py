from app.application.dto.video_topic_dto import VideoTopicResponse
from app.domain.ports.video_topic_repository import VideoTopicRepositoryPort


class ListVideoTopics:
    def __init__(self, topic_repo: VideoTopicRepositoryPort) -> None:
        self.topic_repo = topic_repo

    def execute(self) -> list[VideoTopicResponse]:
        topics = self.topic_repo.list_active()
        return [
            VideoTopicResponse(
                id=topic.code,
                icon=topic.icon,
                label=topic.label,
                desc=topic.description,
            )
            for topic in topics
        ]

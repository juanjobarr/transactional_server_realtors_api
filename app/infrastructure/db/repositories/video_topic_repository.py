from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.video_topic import VideoTopic
from app.domain.ports.video_topic_repository import VideoTopicRepositoryPort
from app.infrastructure.db.models.video_topic_model import VideoTopicModel


class SQLAlchemyVideoTopicRepository(VideoTopicRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[VideoTopic]:
        rows = (
            self.db.query(VideoTopicModel)
            .filter(VideoTopicModel.active.is_(True))
            .order_by(VideoTopicModel.created_at.asc())
            .all()
        )
        return [self._to_entity(row) for row in rows]

    def find_by_code(self, code: str) -> Optional[VideoTopic]:
        row = self.db.query(VideoTopicModel).filter(VideoTopicModel.code == code).first()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: VideoTopicModel) -> VideoTopic:
        return VideoTopic(
            id=str(row.id),
            code=row.code,
            label=row.label,
            description=row.description,
            icon=row.icon,
            active=row.active,
            created_at=row.created_at,
        )

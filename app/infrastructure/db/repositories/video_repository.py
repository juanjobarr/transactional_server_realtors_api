from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.video import Video
from app.domain.ports.video_repository import VideoRepositoryPort
from app.infrastructure.db.models.video_model import VideoModel


class SQLAlchemyVideoRepository(VideoRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, video: Video) -> Video:
        model = VideoModel(
            user_id=video.user_id,
            title=video.title,
            topic_id=video.topic_id,
            draft_id=video.draft_id,
            job_id=video.job_id,
            thumbnail_url=video.thumbnail_url,
            final_video_url=video.final_video_url,
            final_video_storage_key=video.final_video_storage_key,
            format=video.format,
            duration_seconds=video.duration_seconds,
            scenes_count=video.scenes_count,
            views_count=video.views_count,
            downloads_count=video.downloads_count,
            status=video.status,
            published_at=video.published_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def find_by_draft_id(self, draft_id: str) -> Optional[Video]:
        row = (
            self.db.query(VideoModel)
            .filter(VideoModel.draft_id == draft_id)
            .first()
        )
        return self._to_entity(row) if row else None

    def find_by_id_and_user(self, video_id: str, user_id: str) -> Optional[Video]:
        row = (
            self.db.query(VideoModel)
            .filter(VideoModel.id == video_id, VideoModel.user_id == user_id)
            .first()
        )
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: VideoModel) -> Video:
        return Video(
            id=str(row.id),
            user_id=str(row.user_id),
            title=row.title,
            topic_id=str(row.topic_id),
            draft_id=str(row.draft_id) if row.draft_id else None,
            job_id=str(row.job_id) if row.job_id else None,
            thumbnail_url=row.thumbnail_url,
            final_video_url=row.final_video_url,
            final_video_storage_key=row.final_video_storage_key,
            format=row.format,
            duration_seconds=row.duration_seconds,
            scenes_count=row.scenes_count,
            views_count=row.views_count,
            downloads_count=row.downloads_count,
            status=row.status,
            published_at=row.published_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_jobs.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    draft_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_drafts.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(Text, nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("video_topics.id"), nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    final_video_url = Column(Text, nullable=True)
    final_video_storage_key = Column(Text, nullable=True)
    format = Column(Text, nullable=False, default="mp4")
    duration_seconds = Column(Integer, nullable=False, default=0)
    scenes_count = Column(Integer, nullable=False, default=0)
    views_count = Column(Integer, nullable=False, default=0)
    downloads_count = Column(Integer, nullable=False, default=0)
    status = Column(Text, nullable=False, default="published")
    published_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

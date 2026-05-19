import uuid

from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class VideoDraftModel(Base):
    __tablename__ = "video_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("video_topics.id"), nullable=False)
    title = Column(Text, nullable=False)
    subject = Column(Text, nullable=True)
    property_address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    bullet_points_json = Column(JSONB, nullable=False, default=list)
    tone = Column(Text, nullable=False, default="Professional")
    pacing = Column(Text, nullable=False, default="Medium")
    status = Column(Text, nullable=False, default="draft")
    current_step = Column(Text, nullable=False, default="details")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

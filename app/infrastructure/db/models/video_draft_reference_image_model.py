import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class VideoDraftReferenceImageModel(Base):
    __tablename__ = "video_draft_reference_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_drafts.id", ondelete="CASCADE"),
        nullable=False,
    )
    storage_url = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="reference")
    sort_order = Column(Integer, nullable=False, default=0)
    metadata_json = Column(JSONB, nullable=False, default=dict)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

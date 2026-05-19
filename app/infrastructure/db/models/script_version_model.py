import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class ScriptVersionModel(Base):
    __tablename__ = "script_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_drafts.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number = Column(Integer, nullable=False)
    script_text = Column(Text, nullable=False)
    structured_script_json = Column(JSONB, nullable=False, default=dict)
    estimated_read_time_seconds = Column(Integer, nullable=False, default=0)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

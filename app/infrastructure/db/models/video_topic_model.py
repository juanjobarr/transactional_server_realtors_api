import uuid

from sqlalchemy import Boolean, Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class VideoTopicModel(Base):
    __tablename__ = "video_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, nullable=False, unique=True)
    label = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

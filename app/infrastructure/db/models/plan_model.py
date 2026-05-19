import uuid

from sqlalchemy import Boolean, Column, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class PlanModel(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    monthly_video_limit = Column(String, nullable=False)
    monthly_scene_limit = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

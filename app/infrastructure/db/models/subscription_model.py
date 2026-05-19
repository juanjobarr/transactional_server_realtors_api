import uuid

from sqlalchemy import Column, Date, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    billing_start = Column(Date, nullable=False)
    billing_end = Column(Date, nullable=False)
    status = Column(Text, nullable=False, default="active")
    videos_used = Column(Integer, nullable=False, default=0)
    scenes_used = Column(Integer, nullable=False, default=0)
    videos_remaining = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

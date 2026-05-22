import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP

from app.infrastructure.db.base import Base


class WebhookEventModel(Base):
    __tablename__ = "webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(Text, nullable=False)
    external_event_id = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    payload_json = Column(JSONB, nullable=False, default=dict)
    received_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(Text, nullable=False, default="received")

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.domain.entities.webhook_event import WebhookEvent
from app.domain.ports.webhook_event_repository import WebhookEventRepositoryPort
from app.infrastructure.db.models.webhook_event_model import WebhookEventModel


class SQLAlchemyWebhookEventRepository(WebhookEventRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        source: str,
        external_event_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> WebhookEvent:
        model = WebhookEventModel(
            source=source,
            external_event_id=external_event_id,
            event_type=event_type,
            payload_json=payload,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def mark_processed(self, event_id: str, status: str = "processed") -> None:
        self.db.query(WebhookEventModel).filter(WebhookEventModel.id == event_id).update(
            {
                "status": status,
                "processed_at": datetime.now(timezone.utc),
            }
        )
        self.db.commit()

    @staticmethod
    def _to_entity(row: WebhookEventModel) -> WebhookEvent:
        return WebhookEvent(
            id=str(row.id),
            source=row.source,
            external_event_id=row.external_event_id,
            event_type=row.event_type,
            payload=dict(row.payload_json or {}),
            status=row.status,
            received_at=row.received_at,
            processed_at=row.processed_at,
        )

from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.webhook_event import WebhookEvent


class WebhookEventRepositoryPort(ABC):
    @abstractmethod
    def record(
        self,
        *,
        source: str,
        external_event_id: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> WebhookEvent: ...

    @abstractmethod
    def mark_processed(self, event_id: str, status: str = "processed") -> None: ...

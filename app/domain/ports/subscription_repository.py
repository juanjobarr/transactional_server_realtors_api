from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.subscription import Subscription


class SubscriptionRepositoryPort(ABC):
    @abstractmethod
    def find_active_by_user_id(self, user_id: str) -> Optional[Subscription]: ...

    @abstractmethod
    def find_latest_by_user_id(self, user_id: str) -> Optional[Subscription]: ...

    @abstractmethod
    def save(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    def update(self, subscription: Subscription) -> Subscription: ...

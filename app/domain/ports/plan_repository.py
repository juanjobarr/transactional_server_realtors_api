from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.plan import Plan


class PlanRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, plan_id: str) -> Optional[Plan]: ...

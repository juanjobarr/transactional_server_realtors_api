from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.script_version import ScriptVersion


class ScriptVersionRepositoryPort(ABC):
    @abstractmethod
    def create(self, version: ScriptVersion) -> ScriptVersion: ...

    @abstractmethod
    def next_version_number(self, draft_id: str) -> int: ...

    @abstractmethod
    def find_latest_by_draft_id(self, draft_id: str) -> Optional[ScriptVersion]: ...

    @abstractmethod
    def mark_approved(self, version_id: str, approver_user_id: str) -> None: ...

from abc import ABC, abstractmethod

from app.domain.entities.script_version import ScriptVersion


class ScriptVersionRepositoryPort(ABC):
    @abstractmethod
    def create(self, version: ScriptVersion) -> ScriptVersion: ...

    @abstractmethod
    def next_version_number(self, draft_id: str) -> int: ...

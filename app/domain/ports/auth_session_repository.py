from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.auth_session import AuthSession


class AuthSessionRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[AuthSession]: ...

    @abstractmethod
    def find_by_refresh_token_hash(self, token_hash: str) -> Optional[AuthSession]: ...

    @abstractmethod
    def find_active_by_user_id(self, user_id: str) -> list[AuthSession]: ...

    @abstractmethod
    def save(self, session: AuthSession) -> AuthSession: ...

    @abstractmethod
    def revoke(self, session_id: str) -> None: ...

    @abstractmethod
    def revoke_all_for_user(self, user_id: str) -> None: ...

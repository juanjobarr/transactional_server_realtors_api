from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def update(self, user: User) -> User: ...

    @abstractmethod
    def exists_by_email(self, email: str) -> bool: ...

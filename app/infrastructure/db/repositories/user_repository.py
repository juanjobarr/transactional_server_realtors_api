from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.user_status import UserStatus
from app.infrastructure.db.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=str(model.id),
            full_name=model.full_name,
            email=model.email,
            password_hash=model.password_hash,
            avatar_initials=model.avatar_initials or "",
            role=UserRole(model.role),
            status=UserStatus(model.status),
            is_email_verified=model.is_email_verified,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_id(self, user_id: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None

    def save(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            password_hash=user.password_hash,
            avatar_initials=user.avatar_initials,
            role=user.role.value,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, user: User) -> User:
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError(f"User {user.id} not found")
        model.full_name = user.full_name
        model.email = user.email
        model.password_hash = user.password_hash
        model.avatar_initials = user.avatar_initials
        model.role = user.role.value
        model.status = user.status.value
        model.is_email_verified = user.is_email_verified
        model.last_login_at = user.last_login_at
        model.updated_at = user.updated_at
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def exists_by_email(self, email: str) -> bool:
        return (
            self.db.query(UserModel).filter(UserModel.email == email).first() is not None
        )

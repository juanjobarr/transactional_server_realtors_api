from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.auth_session import AuthSession
from app.domain.ports.auth_session_repository import AuthSessionRepositoryPort
from app.infrastructure.db.models.auth_session_model import AuthSessionModel


class SQLAlchemyAuthSessionRepository(AuthSessionRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_entity(self, model: AuthSessionModel) -> AuthSession:
        return AuthSession(
            id=str(model.id),
            user_id=str(model.user_id),
            refresh_token_hash=model.refresh_token_hash,
            device_name=model.device_name,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_by_id(self, session_id: str) -> Optional[AuthSession]:
        model = (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.id == session_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_refresh_token_hash(self, token_hash: str) -> Optional[AuthSession]:
        model = (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.refresh_token_hash == token_hash)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_active_by_user_id(self, user_id: str) -> list[AuthSession]:
        models = (
            self.db.query(AuthSessionModel)
            .filter(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def save(self, session: AuthSession) -> AuthSession:
        model = AuthSessionModel(
            id=session.id,
            user_id=session.user_id,
            refresh_token_hash=session.refresh_token_hash,
            device_name=session.device_name,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def revoke(self, session_id: str) -> None:
        now = datetime.now(timezone.utc)
        model = (
            self.db.query(AuthSessionModel)
            .filter(AuthSessionModel.id == session_id)
            .first()
        )
        if model:
            model.revoked_at = now
            model.updated_at = now
            self.db.commit()

    def revoke_all_for_user(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        self.db.query(AuthSessionModel).filter(
            AuthSessionModel.user_id == user_id,
            AuthSessionModel.revoked_at.is_(None),
        ).update({"revoked_at": now, "updated_at": now})
        self.db.commit()

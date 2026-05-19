import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import LoginUserCommand, TokensResponse
from app.config import settings
from app.domain.entities.auth_session import AuthSession
from app.domain.ports.auth_session_repository import AuthSessionRepositoryPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.password_service import verify_password
from app.domain.services.token_service import TokenService


class LoginUser:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        session_repo: AuthSessionRepositoryPort,
        token_service: TokenService,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.token_service = token_service

    def execute(self, command: LoginUserCommand) -> TokensResponse:
        user = self.user_repo.find_by_email(command.email.lower())
        if not user or not verify_password(command.password, user.password_hash):
            raise ValueError("Invalid credentials")

        refresh_token = self.token_service.create_refresh_token(user.id)
        access_token = self.token_service.create_access_token(user.id, user.role.value)

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        now = datetime.now(timezone.utc)
        session = AuthSession(
            id=str(uuid.uuid4()),
            user_id=user.id,
            refresh_token_hash=token_hash,
            device_name=command.device_name,
            ip_address=command.ip_address,
            user_agent=command.user_agent,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            revoked_at=None,
            created_at=now,
            updated_at=now,
        )
        self.session_repo.save(session)

        user.last_login_at = now
        user.updated_at = now
        self.user_repo.update(user)

        return TokensResponse(access_token=access_token, refresh_token=refresh_token)

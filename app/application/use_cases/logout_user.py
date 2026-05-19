import hashlib

from app.application.dto.auth_dto import LogoutCommand
from app.domain.ports.auth_session_repository import AuthSessionRepositoryPort
from app.domain.services.token_service import TokenService


class LogoutUser:
    def __init__(
        self,
        session_repo: AuthSessionRepositoryPort,
        token_service: TokenService,
    ) -> None:
        self.session_repo = session_repo
        self.token_service = token_service

    def execute(self, command: LogoutCommand) -> None:
        try:
            payload = self.token_service.decode_token(command.refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
        except Exception as exc:
            raise ValueError("Invalid refresh token") from exc

        token_hash = hashlib.sha256(command.refresh_token.encode()).hexdigest()
        session = self.session_repo.find_by_refresh_token_hash(token_hash)

        if session and session.is_valid():
            self.session_repo.revoke(session.id)

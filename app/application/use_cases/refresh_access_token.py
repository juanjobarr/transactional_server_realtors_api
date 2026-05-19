import hashlib

from app.application.dto.auth_dto import RefreshTokenCommand, TokensResponse
from app.domain.ports.auth_session_repository import AuthSessionRepositoryPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.token_service import TokenService


class RefreshAccessToken:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        session_repo: AuthSessionRepositoryPort,
        token_service: TokenService,
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.token_service = token_service

    def execute(self, command: RefreshTokenCommand) -> TokensResponse:
        try:
            payload = self.token_service.decode_token(command.refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            user_id: str = payload["sub"]
        except Exception as exc:
            raise ValueError("Invalid refresh token") from exc

        token_hash = hashlib.sha256(command.refresh_token.encode()).hexdigest()
        session = self.session_repo.find_by_refresh_token_hash(token_hash)

        if not session or not session.is_valid():
            raise ValueError("Session not found or expired")

        user = self.user_repo.find_by_id(user_id)
        if not user or not user.is_active():
            raise ValueError("User not found or inactive")

        new_access_token = self.token_service.create_access_token(user.id, user.role.value)

        return TokensResponse(
            access_token=new_access_token,
            refresh_token=command.refresh_token,
        )

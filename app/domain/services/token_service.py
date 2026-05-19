from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import settings


class TokenService:
    def create_access_token(self, user_id: str, role: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
            "role": role,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError as exc:
            raise ValueError(f"Invalid token: {exc}") from exc

    def get_subject(self, token: str) -> str:
        payload = self.decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise ValueError("Token missing subject")
        return sub

    def get_token_type(self, token: str) -> str:
        payload = self.decode_token(token)
        return payload.get("type", "access")

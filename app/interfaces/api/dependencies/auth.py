from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.services.token_service import TokenService
from app.infrastructure.db.repositories.subscription_repository import (
    SQLAlchemySubscriptionRepository,
)
from app.infrastructure.db.session import get_db

_bearer = HTTPBearer()
_token_service = TokenService()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    token = credentials.credentials
    try:
        payload = _token_service.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
            )
        return user_id
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_active_subscription_user_id(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> str:
    repo = SQLAlchemySubscriptionRepository(db)
    if not repo.find_active_by_user_id(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required",
        )
    return user_id

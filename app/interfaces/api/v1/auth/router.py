from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.application.dto.auth_dto import (
    LoginUserCommand,
    LogoutCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
)
from app.application.use_cases.get_current_user import GetCurrentUser
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.logout_user import LogoutUser
from app.application.use_cases.refresh_access_token import RefreshAccessToken
from app.application.use_cases.register_user import RegisterUser
from app.domain.services.token_service import TokenService
from app.infrastructure.db.repositories.auth_session_repository import (
    SQLAlchemyAuthSessionRepository,
)
from app.infrastructure.db.repositories.plan_repository import SQLAlchemyPlanRepository
from app.infrastructure.db.repositories.subscription_repository import SQLAlchemySubscriptionRepository
from app.infrastructure.db.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.db.session import get_db
from app.interfaces.api.dependencies.auth import get_current_user_id
from app.interfaces.api.v1.auth.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_token_service = TokenService()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    use_case = RegisterUser(
        SQLAlchemyUserRepository(db),
        _token_service,
        SQLAlchemySubscriptionRepository(db),
        SQLAlchemyPlanRepository(db),
    )
    try:
        result = use_case.execute(
            RegisterUserCommand(
                full_name=body.full_name,
                email=str(body.email),
                password=body.password,
            )
        )
    except ValueError as exc:
        msg = str(exc)
        if "already registered" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg) from exc
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=msg) from exc
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    use_case = LoginUser(
        SQLAlchemyUserRepository(db),
        SQLAlchemyAuthSessionRepository(db),
        _token_service,
    )
    try:
        result = use_case.execute(
            LoginUserCommand(
                email=str(body.email),
                password=body.password,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    use_case = RefreshAccessToken(
        SQLAlchemyUserRepository(db),
        SQLAlchemyAuthSessionRepository(db),
        _token_service,
    )
    try:
        result = use_case.execute(RefreshTokenCommand(refresh_token=body.refresh_token))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    use_case = LogoutUser(SQLAlchemyAuthSessionRepository(db), _token_service)
    try:
        use_case.execute(LogoutCommand(refresh_token=body.refresh_token))
    except ValueError:
        pass


@router.get("/me", response_model=UserResponse)
def me(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    use_case = GetCurrentUser(SQLAlchemyUserRepository(db))
    try:
        result = use_case.execute(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserResponse(
        id=result.id,
        full_name=result.full_name,
        email=result.email,
        avatar_initials=result.avatar_initials,
        role=result.role,
        status=result.status,
        is_email_verified=result.is_email_verified,
        last_login_at=result.last_login_at,
        created_at=result.created_at,
    )

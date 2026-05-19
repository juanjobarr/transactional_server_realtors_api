from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RegisterUserCommand:
    full_name: str
    email: str
    password: str


@dataclass
class LoginUserCommand:
    email: str
    password: str
    device_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class RefreshTokenCommand:
    refresh_token: str


@dataclass
class LogoutCommand:
    refresh_token: str


@dataclass
class TokensResponse:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class UserResponse:
    id: str
    full_name: str
    email: str
    avatar_initials: str
    role: str
    status: str
    is_email_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.value_objects.user_role import UserRole
from app.domain.value_objects.user_status import UserStatus


@dataclass
class User:
    id: str
    full_name: str
    email: str
    password_hash: str
    avatar_initials: str
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    @staticmethod
    def build_initials(full_name: str) -> str:
        parts = full_name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        return full_name[:2].upper()

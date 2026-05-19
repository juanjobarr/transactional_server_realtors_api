from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class AuthSession:
    id: str
    user_id: str
    refresh_token_hash: str
    device_name: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    expires_at: datetime
    revoked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        exp = self.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return self.revoked_at is None and exp > now

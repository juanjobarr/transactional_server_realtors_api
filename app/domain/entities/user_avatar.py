from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.value_objects.avatar_status import AvatarStatus


@dataclass
class UserAvatar:
    id: Optional[str]
    user_id: str
    status: AvatarStatus = AvatarStatus.PENDING
    additional_instructions: Optional[str] = None
    reference_image_urls: list[str] = field(default_factory=list)
    avatar_url: Optional[str] = None
    external_job_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

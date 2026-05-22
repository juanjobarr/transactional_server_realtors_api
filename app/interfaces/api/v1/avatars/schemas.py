from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AvatarGenerationResponse(BaseModel):
    avatar_id: str
    status: str
    external_job_id: str
    message: str = "Avatar generation started"


class UserAvatarResponse(BaseModel):
    status: str
    avatar_url: Optional[str] = None
    additional_instructions: Optional[str] = None
    reference_image_urls: list[str] = []
    error_message: Optional[str] = None
    updated_at: Optional[datetime] = None


class AvatarWebhookPayload(BaseModel):
    external_job_id: str
    status: str
    avatar_url: Optional[str] = None
    error_message: Optional[str] = None


class WebhookAck(BaseModel):
    received: bool = True

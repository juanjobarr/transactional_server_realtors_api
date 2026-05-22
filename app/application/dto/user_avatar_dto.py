from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UploadedImage:
    content: bytes
    content_type: str
    filename: str


@dataclass
class GenerateAvatarCommand:
    user_id: str
    additional_instructions: Optional[str]
    images: list[UploadedImage] = field(default_factory=list)


@dataclass
class GenerateAvatarResult:
    avatar_id: str
    status: str
    external_job_id: str


@dataclass
class GetUserAvatarResult:
    status: str
    avatar_url: Optional[str]
    additional_instructions: Optional[str]
    reference_image_urls: list[str]
    error_message: Optional[str]
    updated_at: Optional[datetime]


@dataclass
class ProcessAvatarWebhookCommand:
    external_job_id: str
    status: str
    avatar_url: Optional[str] = None
    error_message: Optional[str] = None

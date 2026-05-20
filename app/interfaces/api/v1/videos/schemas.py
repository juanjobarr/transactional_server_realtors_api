from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VideoTopicResponse(BaseModel):
    id: str
    icon: str
    label: str
    desc: str


class GenerateScriptResponse(BaseModel):
    script: str
    draft_id: str
    script_version_id: str


class VideoLibraryItem(BaseModel):
    draft_id: str
    title: str
    topic_id: str
    topic_code: Optional[str] = None
    status: str
    tone: str
    thumbnail_url: Optional[str] = None
    final_video_url: Optional[str] = None
    has_script: bool
    created_at: Optional[datetime] = None


class VideoLibraryListResponse(BaseModel):
    items: list[VideoLibraryItem]
    total: int
    limit: int
    offset: int
    next_offset: Optional[int] = None


class DraftScriptResponse(BaseModel):
    status: str
    script_text: Optional[str] = None
    script_version_id: Optional[str] = None
    version_number: Optional[int] = None
    message: Optional[str] = None


class UserVideoResponse(BaseModel):
    id: str
    draft_id: Optional[str] = None
    title: str
    topic_id: str
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: int
    status: str
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class ApproveScriptResponse(BaseModel):
    video_id: str
    draft_id: str
    final_video_url: str
    status: str

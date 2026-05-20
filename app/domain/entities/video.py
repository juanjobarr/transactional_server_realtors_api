from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Video:
    id: Optional[str]
    user_id: str
    title: str
    topic_id: str
    final_video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    final_video_storage_key: Optional[str] = None
    job_id: Optional[str] = None
    format: str = "mp4"
    duration_seconds: int = 0
    scenes_count: int = 0
    views_count: int = 0
    downloads_count: int = 0
    status: str = "published"
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    draft_id: Optional[str] = None

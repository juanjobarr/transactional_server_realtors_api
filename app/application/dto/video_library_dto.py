from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ListUserDraftsQuery:
    user_id: str
    limit: int
    offset: int


@dataclass
class UserDraftListItem:
    draft_id: str
    title: str
    topic_id: str
    topic_code: Optional[str]
    status: str
    tone: str
    thumbnail_url: Optional[str]
    final_video_url: Optional[str]
    has_script: bool
    created_at: Optional[datetime]


@dataclass
class ListUserDraftsResult:
    items: list[UserDraftListItem]
    total: int
    limit: int
    offset: int
    next_offset: Optional[int]


@dataclass
class GetDraftScriptQuery:
    draft_id: str
    user_id: str


@dataclass
class GetDraftScriptResult:
    status: str
    script_text: Optional[str] = None
    script_version_id: Optional[str] = None
    version_number: Optional[int] = None
    message: Optional[str] = None


@dataclass
class GetUserVideoQuery:
    draft_id: str
    user_id: str


@dataclass
class ApproveAndGenerateCommand:
    draft_id: str
    user_id: str


@dataclass
class ApproveAndGenerateResult:
    video_id: str
    draft_id: str
    final_video_url: str
    status: str

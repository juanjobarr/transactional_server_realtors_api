from typing import Optional

from app.application.dto.video_library_dto import GetUserVideoQuery
from app.domain.entities.video import Video
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort
from app.domain.ports.video_repository import VideoRepositoryPort


class GetUserVideo:
    def __init__(
        self,
        draft_repo: VideoDraftRepositoryPort,
        video_repo: VideoRepositoryPort,
    ) -> None:
        self.draft_repo = draft_repo
        self.video_repo = video_repo

    def execute(self, query: GetUserVideoQuery) -> Optional[Video]:
        draft = self.draft_repo.find_by_id_and_user(query.draft_id, query.user_id)
        if not draft:
            raise LookupError("Draft not found")

        return self.video_repo.find_by_draft_id(query.draft_id)

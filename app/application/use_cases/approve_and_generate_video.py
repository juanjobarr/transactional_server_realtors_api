from datetime import datetime, timezone

from app.application.dto.video_library_dto import (
    ApproveAndGenerateCommand,
    ApproveAndGenerateResult,
)
from app.config import settings
from app.domain.entities.video import Video
from app.domain.ports.script_version_repository import ScriptVersionRepositoryPort
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort
from app.domain.ports.video_repository import VideoRepositoryPort
from app.domain.value_objects.video_draft_status import VideoDraftStatus


class ApproveAndGenerateVideo:
    def __init__(
        self,
        draft_repo: VideoDraftRepositoryPort,
        script_repo: ScriptVersionRepositoryPort,
        video_repo: VideoRepositoryPort,
    ) -> None:
        self.draft_repo = draft_repo
        self.script_repo = script_repo
        self.video_repo = video_repo

    def execute(self, command: ApproveAndGenerateCommand) -> ApproveAndGenerateResult:
        draft = self.draft_repo.find_by_id_and_user(command.draft_id, command.user_id)
        if not draft:
            raise LookupError("Draft not found")

        if draft.status != VideoDraftStatus.SCRIPTED.value:
            raise ValueError(
                f"Draft is not in scripted state (current: {draft.status})"
            )

        latest_script = self.script_repo.find_latest_by_draft_id(command.draft_id)
        if not latest_script or not latest_script.id:
            raise ValueError("Draft has no script to approve")

        self.script_repo.mark_approved(latest_script.id, command.user_id)

        now = datetime.now(timezone.utc)
        video_entity = Video(
            id=None,
            user_id=command.user_id,
            title=draft.title,
            topic_id=draft.topic_id,
            draft_id=command.draft_id,
            final_video_url=settings.MOCK_GENERATED_VIDEO_URL,
            status="published",
            published_at=now,
        )
        video = self.video_repo.create(video_entity)

        self.draft_repo.update_status(command.draft_id, VideoDraftStatus.GENERATED.value)

        return ApproveAndGenerateResult(
            video_id=video.id or "",
            draft_id=command.draft_id,
            final_video_url=video.final_video_url or "",
            status=VideoDraftStatus.GENERATED.value,
        )

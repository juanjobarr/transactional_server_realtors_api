from app.application.dto.video_library_dto import (
    GetDraftScriptQuery,
    GetDraftScriptResult,
)
from app.domain.ports.script_version_repository import ScriptVersionRepositoryPort
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort


class GetDraftScript:
    def __init__(
        self,
        draft_repo: VideoDraftRepositoryPort,
        script_repo: ScriptVersionRepositoryPort,
    ) -> None:
        self.draft_repo = draft_repo
        self.script_repo = script_repo

    def execute(self, query: GetDraftScriptQuery) -> GetDraftScriptResult:
        draft = self.draft_repo.find_by_id_and_user(query.draft_id, query.user_id)
        if not draft:
            raise LookupError("Draft not found")

        script = self.script_repo.find_latest_by_draft_id(query.draft_id)
        if not script:
            return GetDraftScriptResult(
                status="creating",
                message="Script is being created",
            )

        return GetDraftScriptResult(
            status="ready",
            script_text=script.script_text,
            script_version_id=script.id,
            version_number=script.version_number,
        )

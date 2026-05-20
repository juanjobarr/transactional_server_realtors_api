from app.application.dto.video_library_dto import (
    ListUserDraftsQuery,
    ListUserDraftsResult,
    UserDraftListItem,
)
from app.domain.ports.script_version_repository import ScriptVersionRepositoryPort
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort
from app.domain.ports.video_repository import VideoRepositoryPort
from app.domain.ports.video_topic_repository import VideoTopicRepositoryPort


class ListUserVideoDrafts:
    def __init__(
        self,
        draft_repo: VideoDraftRepositoryPort,
        script_repo: ScriptVersionRepositoryPort,
        video_repo: VideoRepositoryPort,
        topic_repo: VideoTopicRepositoryPort,
    ) -> None:
        self.draft_repo = draft_repo
        self.script_repo = script_repo
        self.video_repo = video_repo
        self.topic_repo = topic_repo

    def execute(self, query: ListUserDraftsQuery) -> ListUserDraftsResult:
        drafts, total = self.draft_repo.list_by_user(
            user_id=query.user_id,
            limit=query.limit,
            offset=query.offset,
        )

        topic_code_by_id = {t.id: t.code for t in self.topic_repo.list_active()}

        items: list[UserDraftListItem] = []
        for draft in drafts:
            assert draft.id is not None
            video = self.video_repo.find_by_draft_id(draft.id)
            has_script = self.script_repo.find_latest_by_draft_id(draft.id) is not None
            items.append(
                UserDraftListItem(
                    draft_id=draft.id,
                    title=draft.title,
                    topic_id=draft.topic_id,
                    topic_code=topic_code_by_id.get(draft.topic_id),
                    status=draft.status,
                    tone=draft.tone,
                    thumbnail_url=video.thumbnail_url if video else None,
                    final_video_url=video.final_video_url if video else None,
                    has_script=has_script,
                    created_at=draft.created_at,
                )
            )

        next_offset = (
            query.offset + len(items)
            if query.offset + len(items) < total
            else None
        )

        return ListUserDraftsResult(
            items=items,
            total=total,
            limit=query.limit,
            offset=query.offset,
            next_offset=next_offset,
        )

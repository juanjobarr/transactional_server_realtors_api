from typing import Optional

from app.application.dto.video_script_dto import (
    GenerateScriptCommand,
    GenerateScriptResponse,
)
from app.domain.entities.script_version import ScriptVersion
from app.domain.entities.video_draft import VideoDraft
from app.domain.ports.image_storage import ImageStoragePort
from app.domain.ports.script_generator import ScriptGeneratorPort
from app.domain.ports.script_version_repository import ScriptVersionRepositoryPort
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort
from app.domain.ports.video_topic_repository import VideoTopicRepositoryPort
from app.domain.value_objects.video_draft_status import VideoDraftStatus


class GenerateVideoScript:
    def __init__(
        self,
        topic_repo: VideoTopicRepositoryPort,
        draft_repo: VideoDraftRepositoryPort,
        version_repo: ScriptVersionRepositoryPort,
        image_storage: ImageStoragePort,
        script_generator: ScriptGeneratorPort,
    ) -> None:
        self.topic_repo = topic_repo
        self.draft_repo = draft_repo
        self.version_repo = version_repo
        self.image_storage = image_storage
        self.script_generator = script_generator

    def execute(self, command: GenerateScriptCommand) -> GenerateScriptResponse:
        topic = self.topic_repo.find_by_code(command.topic_code)
        if not topic:
            raise ValueError(f"Topic not found: {command.topic_code}")

        image_url: Optional[str] = None
        if command.reference_image_bytes and command.reference_image_mime:
            image_url = self.image_storage.upload(
                content=command.reference_image_bytes,
                content_type=command.reference_image_mime,
                filename_hint=command.reference_image_filename or "image",
            )

        draft_entity = VideoDraft(
            id=None,
            user_id=command.user_id,
            topic_id=topic.id,
            title=command.title or "Untitled",
            tone=command.tone,
            pacing="Medium",
            status=VideoDraftStatus.DRAFTED.value,
            current_step="script",
            description=command.notes,
        )
        draft = self.draft_repo.create(draft_entity)

        if image_url and draft.id:
            self.draft_repo.add_reference_image(
                draft_id=draft.id,
                storage_url=image_url,
                role="reference",
                sort_order=0,
            )

        script_text = self.script_generator.generate(
            topic_code=topic.code,
            topic_label=topic.label,
            title=command.title,
            notes=command.notes,
            tone=command.tone,
            reference_image_bytes=command.reference_image_bytes,
            reference_image_mime=command.reference_image_mime,
        )

        version_entity = ScriptVersion(
            id=None,
            draft_id=draft.id or "",
            version_number=1,
            script_text=script_text,
        )
        version = self.version_repo.create(version_entity)

        if draft.id:
            self.draft_repo.update_status(draft.id, VideoDraftStatus.SCRIPTED.value)

        return GenerateScriptResponse(
            script=script_text,
            draft_id=draft.id or "",
            script_version_id=version.id or "",
        )

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.application.dto.video_script_dto import GenerateScriptCommand
from app.application.use_cases.generate_video_script import GenerateVideoScript
from app.application.use_cases.list_video_topics import ListVideoTopics
from app.infrastructure.clients.azure_blob_image_storage import AzureBlobImageStorage
from app.infrastructure.clients.azure_openai_script_generator import (
    AzureOpenAIScriptGenerator,
)
from app.infrastructure.db.repositories.script_version_repository import (
    SQLAlchemyScriptVersionRepository,
)
from app.infrastructure.db.repositories.video_draft_repository import (
    SQLAlchemyVideoDraftRepository,
)
from app.infrastructure.db.repositories.video_topic_repository import (
    SQLAlchemyVideoTopicRepository,
)
from app.infrastructure.db.session import get_db
from app.interfaces.api.dependencies.auth import get_current_user_id
from app.interfaces.api.v1.videos.schemas import (
    GenerateScriptResponse,
    VideoTopicResponse,
)

router = APIRouter(prefix="/videos", tags=["videos"])

_ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@router.get("/topics", response_model=list[VideoTopicResponse])
def list_topics(db: Session = Depends(get_db)) -> list[VideoTopicResponse]:
    use_case = ListVideoTopics(SQLAlchemyVideoTopicRepository(db))
    topics = use_case.execute()
    return [
        VideoTopicResponse(id=t.id, icon=t.icon, label=t.label, desc=t.desc)
        for t in topics
    ]


@router.post("/script", response_model=GenerateScriptResponse)
def generate_script(
    topic_id: str = Form(...),
    tone: str = Form(...),
    title: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    reference_image: Optional[UploadFile] = File(None),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> GenerateScriptResponse:
    image_bytes: Optional[bytes] = None
    image_mime: Optional[str] = None
    image_filename: Optional[str] = None

    if reference_image is not None:
        if reference_image.content_type not in _ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported image type '{reference_image.content_type}'. "
                    f"Allowed: {sorted(_ALLOWED_IMAGE_MIMES)}"
                ),
            )
        image_bytes = reference_image.file.read()
        image_mime = reference_image.content_type
        image_filename = reference_image.filename

    use_case = GenerateVideoScript(
        SQLAlchemyVideoTopicRepository(db),
        SQLAlchemyVideoDraftRepository(db),
        SQLAlchemyScriptVersionRepository(db),
        AzureBlobImageStorage(),
        AzureOpenAIScriptGenerator(),
    )

    try:
        result = use_case.execute(
            GenerateScriptCommand(
                user_id=user_id,
                topic_code=topic_id,
                tone=tone,
                title=title,
                notes=notes,
                reference_image_bytes=image_bytes,
                reference_image_mime=image_mime,
                reference_image_filename=image_filename,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return GenerateScriptResponse(
        script=result.script,
        draft_id=result.draft_id,
        script_version_id=result.script_version_id,
    )

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.application.dto.video_library_dto import (
    ApproveAndGenerateCommand,
    GetDraftScriptQuery,
    GetUserVideoQuery,
    ListUserDraftsQuery,
)
from app.application.dto.video_script_dto import GenerateScriptCommand
from app.application.use_cases.approve_and_generate_video import ApproveAndGenerateVideo
from app.application.use_cases.generate_video_script import GenerateVideoScript
from app.application.use_cases.get_draft_script import GetDraftScript
from app.application.use_cases.get_user_video import GetUserVideo
from app.application.use_cases.list_user_video_drafts import ListUserVideoDrafts
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
from app.infrastructure.db.repositories.video_repository import SQLAlchemyVideoRepository
from app.infrastructure.db.repositories.video_topic_repository import (
    SQLAlchemyVideoTopicRepository,
)
from app.infrastructure.db.session import get_db
from app.interfaces.api.dependencies.auth import (
    get_active_subscription_user_id,
    get_current_user_id,
)
from app.interfaces.api.v1.videos.schemas import (
    ApproveScriptResponse,
    DraftScriptResponse,
    GenerateScriptResponse,
    UserVideoResponse,
    VideoLibraryItem,
    VideoLibraryListResponse,
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


@router.get("", response_model=VideoLibraryListResponse)
def list_user_videos(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> VideoLibraryListResponse:
    use_case = ListUserVideoDrafts(
        SQLAlchemyVideoDraftRepository(db),
        SQLAlchemyScriptVersionRepository(db),
        SQLAlchemyVideoRepository(db),
        SQLAlchemyVideoTopicRepository(db),
    )
    result = use_case.execute(
        ListUserDraftsQuery(user_id=user_id, limit=limit, offset=offset)
    )
    return VideoLibraryListResponse(
        items=[
            VideoLibraryItem(
                draft_id=item.draft_id,
                title=item.title,
                topic_id=item.topic_id,
                topic_code=item.topic_code,
                status=item.status,
                tone=item.tone,
                thumbnail_url=item.thumbnail_url,
                final_video_url=item.final_video_url,
                has_script=item.has_script,
                created_at=item.created_at,
            )
            for item in result.items
        ],
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        next_offset=result.next_offset,
    )


@router.get("/{draft_id}/script", response_model=DraftScriptResponse)
def get_draft_script(
    draft_id: str,
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> DraftScriptResponse:
    use_case = GetDraftScript(
        SQLAlchemyVideoDraftRepository(db),
        SQLAlchemyScriptVersionRepository(db),
    )
    try:
        result = use_case.execute(
            GetDraftScriptQuery(draft_id=draft_id, user_id=user_id)
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return DraftScriptResponse(
        status=result.status,
        script_text=result.script_text,
        script_version_id=result.script_version_id,
        version_number=result.version_number,
        message=result.message,
    )


@router.get("/{draft_id}/final", response_model=UserVideoResponse)
def get_user_video_final(
    draft_id: str,
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> UserVideoResponse:
    use_case = GetUserVideo(
        SQLAlchemyVideoDraftRepository(db),
        SQLAlchemyVideoRepository(db),
    )
    try:
        video = use_case.execute(
            GetUserVideoQuery(draft_id=draft_id, user_id=user_id)
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not yet generated",
        )

    return UserVideoResponse(
        id=video.id or "",
        draft_id=video.draft_id,
        title=video.title,
        topic_id=video.topic_id,
        final_video_url=video.final_video_url,
        thumbnail_url=video.thumbnail_url,
        duration_seconds=video.duration_seconds,
        status=video.status,
        published_at=video.published_at,
        created_at=video.created_at,
    )


@router.post("/{draft_id}/approve", response_model=ApproveScriptResponse)
def approve_and_generate_video(
    draft_id: str,
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> ApproveScriptResponse:
    use_case = ApproveAndGenerateVideo(
        SQLAlchemyVideoDraftRepository(db),
        SQLAlchemyScriptVersionRepository(db),
        SQLAlchemyVideoRepository(db),
    )
    try:
        result = use_case.execute(
            ApproveAndGenerateCommand(draft_id=draft_id, user_id=user_id)
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    return ApproveScriptResponse(
        video_id=result.video_id,
        draft_id=result.draft_id,
        final_video_url=result.final_video_url,
        status=result.status,
    )

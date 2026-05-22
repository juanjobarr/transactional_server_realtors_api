from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.application.dto.user_avatar_dto import (
    GenerateAvatarCommand,
    ProcessAvatarWebhookCommand,
    UploadedImage,
)
from app.application.use_cases.generate_avatar import GenerateAvatar
from app.application.use_cases.get_user_avatar import GetUserAvatar
from app.application.use_cases.process_avatar_webhook import ProcessAvatarWebhook
from app.config import settings
from app.infrastructure.clients.azure_blob_image_storage import AzureBlobImageStorage
from app.infrastructure.clients.external_avatar_generator import HttpAvatarGenerator
from app.infrastructure.db.repositories.user_avatar_repository import (
    SQLAlchemyUserAvatarRepository,
)
from app.infrastructure.db.repositories.webhook_event_repository import (
    SQLAlchemyWebhookEventRepository,
)
from app.infrastructure.db.session import get_db
from app.interfaces.api.dependencies.auth import get_active_subscription_user_id
from app.interfaces.api.v1.avatars.schemas import (
    AvatarGenerationResponse,
    AvatarWebhookPayload,
    UserAvatarResponse,
    WebhookAck,
)

router = APIRouter(prefix="/avatars", tags=["avatars"])

_ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


@router.post(
    "",
    response_model=AvatarGenerationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def generate_avatar(
    additional_instructions: Optional[str] = Form(None),
    images: list[UploadFile] = File(...),
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> AvatarGenerationResponse:
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one reference image is required",
        )
    if len(images) > settings.AVATAR_MAX_REFERENCE_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Too many images. Max allowed: {settings.AVATAR_MAX_REFERENCE_IMAGES}"
            ),
        )
    if additional_instructions and len(additional_instructions) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="additional_instructions exceeds 2000 characters",
        )

    uploaded: list[UploadedImage] = []
    for img in images:
        if img.content_type not in _ALLOWED_IMAGE_MIMES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported image type '{img.content_type}'. "
                    f"Allowed: {sorted(_ALLOWED_IMAGE_MIMES)}"
                ),
            )
        content = img.file.read()
        if len(content) > settings.AVATAR_MAX_IMAGE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Image '{img.filename}' exceeds max size "
                    f"({settings.AVATAR_MAX_IMAGE_BYTES} bytes)"
                ),
            )
        uploaded.append(
            UploadedImage(
                content=content,
                content_type=img.content_type,
                filename=img.filename or "image",
            )
        )

    use_case = GenerateAvatar(
        SQLAlchemyUserAvatarRepository(db),
        AzureBlobImageStorage(),
        HttpAvatarGenerator(),
    )

    try:
        result = use_case.execute(
            GenerateAvatarCommand(
                user_id=user_id,
                additional_instructions=additional_instructions,
                images=uploaded,
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Avatar service error: {exc}",
        ) from exc

    return AvatarGenerationResponse(
        avatar_id=result.avatar_id,
        status=result.status,
        external_job_id=result.external_job_id,
    )


@router.get("/me", response_model=UserAvatarResponse)
def get_my_avatar(
    user_id: str = Depends(get_active_subscription_user_id),
    db: Session = Depends(get_db),
) -> UserAvatarResponse:
    use_case = GetUserAvatar(SQLAlchemyUserAvatarRepository(db))
    try:
        result = use_case.execute(user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return UserAvatarResponse(
        status=result.status,
        avatar_url=result.avatar_url,
        additional_instructions=result.additional_instructions,
        reference_image_urls=result.reference_image_urls,
        error_message=result.error_message,
        updated_at=result.updated_at,
    )


@router.post("/webhook", response_model=WebhookAck)
def avatar_webhook(
    payload: AvatarWebhookPayload,
    db: Session = Depends(get_db),
) -> WebhookAck:
    # TODO: add bearer/HMAC auth before exposing publicly. Today the avatar
    # service is internal-only.
    use_case = ProcessAvatarWebhook(
        SQLAlchemyUserAvatarRepository(db),
        AzureBlobImageStorage(),
        SQLAlchemyWebhookEventRepository(db),
    )
    try:
        use_case.execute(
            ProcessAvatarWebhookCommand(
                external_job_id=payload.external_job_id,
                status=payload.status,
                avatar_url=payload.avatar_url,
                error_message=payload.error_message,
            )
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    return WebhookAck()

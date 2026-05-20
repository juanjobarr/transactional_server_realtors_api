from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.video_draft import VideoDraft
from app.domain.ports.video_draft_repository import VideoDraftRepositoryPort
from app.infrastructure.db.models.video_draft_model import VideoDraftModel
from app.infrastructure.db.models.video_draft_reference_image_model import (
    VideoDraftReferenceImageModel,
)


class SQLAlchemyVideoDraftRepository(VideoDraftRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, draft: VideoDraft) -> VideoDraft:
        model = VideoDraftModel(
            user_id=draft.user_id,
            topic_id=draft.topic_id,
            title=draft.title,
            subject=draft.subject,
            property_address=draft.property_address,
            description=draft.description,
            bullet_points_json=draft.bullet_points,
            tone=draft.tone,
            pacing=draft.pacing,
            status=draft.status,
            current_step=draft.current_step,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def add_reference_image(
        self,
        draft_id: str,
        storage_url: str,
        role: str = "reference",
        sort_order: int = 0,
    ) -> None:
        model = VideoDraftReferenceImageModel(
            draft_id=draft_id,
            storage_url=storage_url,
            role=role,
            sort_order=sort_order,
        )
        self.db.add(model)
        self.db.commit()

    def list_by_user(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> tuple[list[VideoDraft], int]:
        total = (
            self.db.query(func.count(VideoDraftModel.id))
            .filter(VideoDraftModel.user_id == user_id)
            .scalar()
        ) or 0
        rows = (
            self.db.query(VideoDraftModel)
            .filter(VideoDraftModel.user_id == user_id)
            .order_by(VideoDraftModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_entity(r) for r in rows], total

    def find_by_id_and_user(
        self,
        draft_id: str,
        user_id: str,
    ) -> Optional[VideoDraft]:
        row = (
            self.db.query(VideoDraftModel)
            .filter(
                VideoDraftModel.id == draft_id,
                VideoDraftModel.user_id == user_id,
            )
            .first()
        )
        return self._to_entity(row) if row else None

    def update_status(self, draft_id: str, status: str) -> None:
        self.db.query(VideoDraftModel).filter(VideoDraftModel.id == draft_id).update(
            {
                "status": status,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        self.db.commit()

    @staticmethod
    def _to_entity(row: VideoDraftModel) -> VideoDraft:
        return VideoDraft(
            id=str(row.id),
            user_id=str(row.user_id),
            topic_id=str(row.topic_id),
            title=row.title,
            subject=row.subject,
            property_address=row.property_address,
            description=row.description,
            bullet_points=list(row.bullet_points_json or []),
            tone=row.tone,
            pacing=row.pacing,
            status=row.status,
            current_step=row.current_step,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

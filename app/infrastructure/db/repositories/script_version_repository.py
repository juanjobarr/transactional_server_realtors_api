from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.script_version import ScriptVersion
from app.domain.ports.script_version_repository import ScriptVersionRepositoryPort
from app.infrastructure.db.models.script_version_model import ScriptVersionModel


class SQLAlchemyScriptVersionRepository(ScriptVersionRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, version: ScriptVersion) -> ScriptVersion:
        model = ScriptVersionModel(
            draft_id=version.draft_id,
            version_number=version.version_number,
            script_text=version.script_text,
            structured_script_json=version.structured_script,
            estimated_read_time_seconds=version.estimated_read_time_seconds,
            is_approved=version.is_approved,
            approved_by_user_id=version.approved_by_user_id,
            approved_at=version.approved_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def next_version_number(self, draft_id: str) -> int:
        current_max = (
            self.db.query(func.max(ScriptVersionModel.version_number))
            .filter(ScriptVersionModel.draft_id == draft_id)
            .scalar()
        )
        return (current_max or 0) + 1

    @staticmethod
    def _to_entity(row: ScriptVersionModel) -> ScriptVersion:
        return ScriptVersion(
            id=str(row.id),
            draft_id=str(row.draft_id),
            version_number=row.version_number,
            script_text=row.script_text,
            structured_script=dict(row.structured_script_json or {}),
            estimated_read_time_seconds=row.estimated_read_time_seconds,
            is_approved=row.is_approved,
            approved_by_user_id=str(row.approved_by_user_id) if row.approved_by_user_id else None,
            approved_at=row.approved_at,
            created_at=row.created_at,
        )

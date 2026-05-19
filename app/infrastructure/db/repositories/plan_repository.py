from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.plan import Plan
from app.domain.ports.plan_repository import PlanRepositoryPort
from app.infrastructure.db.models.plan_model import PlanModel


class SQLAlchemyPlanRepository(PlanRepositoryPort):
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        row = self.db.query(PlanModel).filter(PlanModel.id == plan_id).first()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row: PlanModel) -> Plan:
        return Plan(
            id=str(row.id),
            name=row.name,
            monthly_video_limit=int(row.monthly_video_limit),
            monthly_scene_limit=int(row.monthly_scene_limit),
            price=row.price,
            currency=row.currency,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

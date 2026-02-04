from sqlalchemy.orm import Session, joinedload
from app.db.models import ReportExecution
from typing import List
import uuid


def get_executions_service(
    db: Session, template_id: str | None = None
) -> List[ReportExecution]:
    """
    Obtiene las ejecuciones con la información del template incluida mediante join.
    """
    query = db.query(ReportExecution).options(joinedload(ReportExecution.template))

    if template_id:
        try:
            template_uuid = uuid.UUID(template_id)
            query = query.filter(ReportExecution.template_id == template_uuid)
        except ValueError:
            return []

    return query.order_by(ReportExecution.executed_at.desc()).all()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.db import get_db
from app.db.schema import ExecutionResponse, TemplateInfo
from app.services.service_get_executions import get_executions_service
import uuid

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/executions", response_model=List[ExecutionResponse])
def get_executions(template_id: str | None = None, db: Session = Depends(get_db)):
    """
    Obtiene todas las ejecuciones o las de un template específico con información completa del template.
    """
    validated_template_id = None
    if template_id:
        try:
            validated_template_id = str(uuid.UUID(template_id))
        except ValueError:
            raise HTTPException(
                status_code=400, detail="template_id debe ser un UUID válido"
            )

    executions = get_executions_service(db, validated_template_id)

    return [
        ExecutionResponse(
            execution_id=str(e.id),
            template_id=str(e.template_id) if e.template_id else None,  # pyright: ignore
            template_info=TemplateInfo(
                id=str(e.template.id),
                name=e.template.name,
                description=e.template.description,
                sql_template=e.template.sql_template,
            )
            if e.template
            else None,
            executed_query=e.executed_query,  # pyright: ignore
            parameters=e.parameters,  # pyright: ignore
            status=e.status,  # pyright: ignore
            row_count=e.row_count,  # pyright: ignore
            error_message=e.error_message,  # pyright: ignore
            executed_at=e.executed_at.isoformat(),
        )
        for e in executions
    ]

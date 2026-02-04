from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.schema import ExecuteTemplateRequest, ExecuteTemplateResponse
from app.db.db import get_db
from app.db.models import ReportExecution
from app.services.service_execute_template import execute_template_service

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/{template_id}/execute", response_model=ExecuteTemplateResponse)
def execute_template(
    template_id: str,
    request: ExecuteTemplateRequest,
    db: Session = Depends(get_db),
):
    try:
        execution: ReportExecution = execute_template_service(
            db=db, template_id=template_id, parameters=request.parameters
        )
        return ExecuteTemplateResponse(
            execution_id=str(execution.id),
            template_id=str(execution.template_id),
            status=execution.status,  # pyright: ignore
            row_count=execution.row_count,  # pyright: ignore
            error_message=execution.error_message,  # pyright: ignore
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando template: {e}")

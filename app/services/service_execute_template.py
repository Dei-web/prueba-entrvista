from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.db.models import QueryTemplate, ReportExecution


def execute_template_service(
    db: Session, template_id: str, parameters: dict
) -> ReportExecution:
    """
    Ejecuta un QueryTemplate con parámetros y guarda el resultado en report_executions.
    """
    try:
        template = (
            db.query(QueryTemplate).filter(QueryTemplate.id == template_id).first()
        )
        if not template:
            raise ValueError(f"Template con id {template_id} no encontrado")

        try:
            result = db.execute(text(template.sql_template), parameters)  # pyright: ignore
            row_count = result.rowcount  # pyright: ignore
            status = "SUCCESS"
            error_message = None
        except Exception as exec_error:
            row_count = None
            status = "FAILED"
            error_message = str(exec_error)

        execution = ReportExecution(
            template_id=template.id,
            executed_query=template.sql_template,
            parameters=parameters,
            status=status,
            row_count=row_count,
            error_message=error_message,
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        return execution

    except SQLAlchemyError as e:
        db.rollback()
        raise e

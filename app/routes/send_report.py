from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.db import get_db
from app.services.service_get_executions import get_executions_service
from app.services.service_email import send_execution_email

router = APIRouter(prefix="/templates", tags=["Templates"])


class EmailRequest(BaseModel):
    to_email: EmailStr


@router.post("/{template_id}/send_email")
def send_template_execution_email(
    template_id: str, email_request: EmailRequest, db: Session = Depends(get_db)
):
    """
    Envía un reporte de ejecuciones por correo electrónico en formato CSV.
    """
    try:
        # Obtener las ejecuciones con el join del template
        executions = get_executions_service(db, template_id)

        if not executions:
            raise HTTPException(
                status_code=404,
                detail=f"No hay ejecuciones para el template {template_id}.",
            )

        # Verificar que al menos una ejecución tenga el template cargado
        print(f"Enviando {len(executions)} ejecuciones")
        for e in executions:
            print(
                f"Execution {e.id}: template={e.template.name if e.template else 'NO TEMPLATE'}"
            )

        # Enviar el correo con el CSV adjunto
        result = send_execution_email(executions, email_request.to_email)

        return {
            "success": True,
            "message": f"Correo enviado exitosamente a {email_request.to_email}",
            "executions_count": len(executions),
            "email_id": result.get("id") if isinstance(result, dict) else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completo: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error al enviar el correo: {str(e)}"
        )

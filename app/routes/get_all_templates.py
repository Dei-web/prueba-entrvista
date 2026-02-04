from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.db import get_db
from app.services.service_get_template import get_all_templates_service

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("/all")
def get_all_templates(
    db: Session = Depends(get_db),
):
    try:
        template = get_all_templates_service(db)

        return {
            "message": "Templates obtenidos",
            "data": template,
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.db import get_db
from app.db.schema import QueryTemplateCreate
from app.services.service_create_template import create_template_service

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/")
def create_template(
    data: QueryTemplateCreate,
    db: Session = Depends(get_db),
):
    try:
        template = create_template_service(db, data)

        return {
            "message": "Template creado",
            "data": template,
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

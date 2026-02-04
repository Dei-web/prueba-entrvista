from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import QueryTemplate
from app.db.schema import QueryTemplateCreate


def create_template_service(db: Session, data: QueryTemplateCreate) -> QueryTemplate:
    try:
        template = QueryTemplate(
            name=data.name,
            description=data.description,
            sql_template=data.sql_template,
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        return template

    except SQLAlchemyError as e:
        db.rollback()
        raise e

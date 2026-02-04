from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models import QueryTemplate


def get_all_templates_service(db: Session) -> list[QueryTemplate]:
    """
    Retorna todos los QueryTemplates de la base de datos
    """
    try:
        templates = db.query(QueryTemplate).all()
        return templates
    except SQLAlchemyError as e:
        raise e

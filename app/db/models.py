import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    Integer,
    Numeric,
    Date,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.db import Base


class QueryTemplate(Base):
    __tablename__ = "query_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sql_template = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    executions = relationship("ReportExecution", back_populates="template")


class ReportExecution(Base):
    __tablename__ = "report_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("query_templates.id", ondelete="SET NULL"),
    )

    executed_query = Column(Text, nullable=False)
    parameters = Column(JSONB)

    status = Column(String(20), nullable=False)
    row_count = Column(Integer)

    error_message = Column(Text)
    executed_at = Column(TIMESTAMP, server_default=func.now())

    template = relationship("QueryTemplate", back_populates="executions")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String(100))
    producto = Column(String(100))
    monto = Column(Numeric(10, 2))
    fecha = Column(Date)

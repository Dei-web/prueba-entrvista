import uuid
from datetime import datetime, date
from typing import Optional, Dict, Any
from pydantic import BaseModel


class QueryTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    sql_template: str


class QueryTemplateCreate(QueryTemplateBase):
    pass


class QueryTemplateRead(QueryTemplateBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ReportExecutionBase(BaseModel):
    template_id: Optional[uuid.UUID] = None
    executed_query: str
    parameters: Optional[Dict[str, Any]] = None
    status: str
    row_count: Optional[int] = None
    error_message: Optional[str] = None


class ReportExecutionCreate(ReportExecutionBase):
    pass


class ReportExecutionRead(ReportExecutionBase):
    id: uuid.UUID
    executed_at: datetime

    class Config:
        from_attributes = True


class VentaBase(BaseModel):
    cliente: str
    producto: str
    monto: float
    fecha: date


class VentaRead(VentaBase):
    id: int

    class Config:
        from_attributes = True


class ExecuteTemplateRequest(BaseModel):
    parameters: Dict[str, Any] = {}


class ExecuteTemplateResponse(BaseModel):
    execution_id: str
    template_id: str
    status: str
    row_count: int | None
    error_message: str | None


# Nuevo schema para información básica del template
class TemplateInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sql_template: Optional[str] = None

    class Config:
        from_attributes = True


# Schema actualizado con información del template
class ExecutionResponse(BaseModel):
    execution_id: str
    template_id: str | None
    template_info: Optional[TemplateInfo] = None  # Información del template
    executed_query: Optional[str] = None  # Query ejecutada
    parameters: Optional[Dict[str, Any]] = None  # Parámetros usados
    status: str
    row_count: int | None
    error_message: str | None
    executed_at: str

    class Config:
        from_attributes = True

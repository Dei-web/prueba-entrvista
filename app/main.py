from fastapi import FastAPI
from app.routes import templates
from app.routes import get_all_templates
from app.routes import get_executions
from app.routes import execute_template
from app.routes import send_report

app = FastAPI()

app.include_router(templates.router)
app.include_router(get_executions.router)
app.include_router(send_report.router)
app.include_router(get_all_templates.router)
app.include_router(execute_template.router)

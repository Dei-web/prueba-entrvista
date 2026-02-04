import csv
import io
import base64
import os
import resend
from typing import List
from app.db.models import ReportExecution

resend.api_key = os.getenv("RESEND")


def send_execution_email(
    executions: List[ReportExecution],
    to: str,
    subject: str = "Reporte de Ejecuciones",
    from_email: str = "E-commerce Dei <onboarding@resend.dev>",
):
    """
    Envía por correo las ejecuciones en formato CSV adjunto usando Resend.
    """
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)

    # Headers del CSV
    writer.writerow(
        [
            "Execution ID",
            "Template ID",
            "Template Name",
            "Template Description",
            "SQL Template",
            "Executed Query",
            "Parameters",
            "Status",
            "Row Count",
            "Error",
            "Executed At",
        ]
    )

    for e in executions:
        writer.writerow(
            [
                str(e.id),
                str(e.template_id) if e.template_id else "N/A",
                e.template.name if e.template else "N/A",
                e.template.description if e.template else "N/A",
                e.template.sql_template if e.template else "N/A",
                e.executed_query if e.executed_query else "N/A",
                str(e.parameters) if e.parameters else "{}",
                e.status if e.status else "N/A",
                str(e.row_count) if e.row_count is not None else "0",
                e.error_message if e.error_message else "",
                e.executed_at.isoformat() if e.executed_at else "N/A",
            ]
        )

    # Convertir a base64
    csv_content = csv_buffer.getvalue().encode("utf-8")
    csv_base64 = base64.b64encode(csv_content).decode("utf-8")

    # Parámetros del email
    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": [to],
        "subject": subject,
        "text": f"Adjunto encontrarás el reporte de ejecuciones con {len(executions)} registro(s).",
        "attachments": [
            {
                "filename": "report.csv",
                "content": csv_base64,
            }
        ],
    }

    return resend.Emails.send(params)

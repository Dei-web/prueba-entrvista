# Documentación de endpoints - prueba-entrvista

Este documento resume los endpoints expuestos en la aplicación (revisado desde `app/routes/`). Todas las rutas usan JSON como body de entrada/salida y dependen de la sesión de BD proporcionada por la dependencia `get_db`.

Base prefix de rutas: `/templates`

---

## 1) Crear template
- Método: POST
- Path: `/templates/`
- Tag: Templates
- Descripción: Crea un nuevo template de consulta (nombre, descripción, SQL).
- Body (JSON):
  - name: string (requerido)
  - description: string (opcional)
  - sql_template: string (requerido)
- Respuesta (200):
  - {
      "message": "Template creado",
      "data": { ... objeto template creado ... }
    }
- Errores:
  - 500: Error de SQL / error interno.

Ejemplo curl:
```bash
curl -X POST "http://<HOST>/templates/" \
  -H "Content-Type: application/json" \
  -d '{"name":"Reporte ventas", "description":"Reporte mensual", "sql_template":"SELECT * FROM ventas;"}'
```

---

## 2) Obtener todos los templates
- Método: GET
- Path: `/templates/all`
- Tag: Templates
- Descripción: Devuelve todos los templates registrados.
- Parámetros: ninguno
- Respuesta (200):
  - {
      "message": "Templates obtenidos",
      "data": [ ... lista de templates ... ]
    }
- Errores:
  - 500: Error de SQL / error interno.

Ejemplo curl:
```bash
curl "http://<HOST>/templates/all"
```

---

## 3) Obtener ejecuciones
- Método: GET
- Path: `/templates/executions`
- Tag: Templates
- Descripción: Obtiene todas las ejecuciones o, si se provee, las ejecuciones de un template específico.
- Query params:
  - template_id (opcional): UUID del template para filtrar.
- Respuesta (200): Lista de ExecutionResponse (JSON array). Cada elemento tiene:
  - execution_id: string
  - template_id: string | null
  - template_info: objeto con { id, name, description?, sql_template? } | null
  - executed_query: string | null
  - parameters: object | null
  - status: string
  - row_count: int | null
  - error_message: string | null
  - executed_at: string (ISO)
- Errores:
  - 400: Si `template_id` está presente y no es un UUID válido.
  - 500: Error interno.

Ejemplo curl (todas las ejecuciones):
```bash
curl "http://<HOST>/templates/executions"
```

Ejemplo curl (filtro por template_id):
```bash
curl "http://<HOST>/templates/executions?template_id=11111111-2222-3333-4444-555555555555"
```

---

## 4) Ejecutar un template
- Método: POST
- Path: `/templates/{template_id}/execute`
- Tag: Templates
- Descripción: Ejecuta el SQL del template indicado con parámetros opcionales y registra la ejecución.
- Path params:
  - template_id: UUID del template a ejecutar
- Body (JSON):
  - parameters: object (mapa de parámetros que el SQL puede usar). Por defecto un objeto vacío.
    Ejemplo: `{ "start_date": "2025-01-01", "end_date": "2025-01-31" }`
- Respuesta (200): ExecuteTemplateResponse
  - execution_id: string
  - template_id: string
  - status: string (por ejemplo: "success", "failed", etc.)
  - row_count: int | null
  - error_message: string | null
- Errores:
  - 404: Si el template no existe (lanza ValueError internamente).
  - 500: Error ejecutando template / error interno.

Ejemplo curl:
```bash
curl -X POST "http://<HOST>/templates/11111111-2222-3333-4444-555555555555/execute" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"start_date":"2025-01-01", "end_date":"2025-01-31"}}'
```

---

## 5) Enviar ejecuciones por correo (CSV)
- Método: POST
- Path: `/templates/{template_id}/send_email`
- Tag: Templates
- Descripción: Recupera las ejecuciones del template y envía un CSV con los resultados al correo indicado (usa el servicio Resend configurado mediante `RESEND` env var en `service_email`).
- Path params:
  - template_id: UUID del template
- Body (JSON):
  - to_email: string (e-mail válido)
- Respuesta (200): JSON con al menos `success: true` si el envío fue correcto.
- Errores:
  - 404: Si no hay ejecuciones para el template solicitado.
  - 500: Error al enviar correo o error interno.

Ejemplo curl:
```bash
curl -X POST "http://<HOST>/templates/11111111-2222-3333-4444-555555555555/send_email" \
  -H "Content-Type: application/json" \
  -d '{"to_email":"destino@ejemplo.com"}'
```

---


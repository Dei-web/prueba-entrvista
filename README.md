# Documentación de endpoints - prueba-entrevista

Este documento resume los endpoints expuestos en la aplicación (revisado desde `app/routes/`). Todas las rutas usan JSON como body de entrada/salida y dependen de la sesión de BD proporcionada por la dependencia `get_db`.

Base prefix de rutas: `/templates`

## Requisitos previos

### Variables de entorno requeridas
La aplicación está dockerizada y requiere las siguientes variables de entorno en el archivo `.env`:

```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://user:password@db:5432/dbname

# API de Resend (requerido para envío de emails)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
```

### Obtener API Key de Resend
1. Regístrate en https://resend.com
2. Crea una API Key en el dashboard
3. Agrega la key al archivo `.env` como `RESEND_API_KEY`
4. **Importante**: El email remitente debe estar verificado en Resend o usar el dominio de desarrollo `onboarding@resend.dev`

### Docker
La aplicación se ejecuta con Docker Compose:
```bash
docker-compose up -d
```

Servicios incluidos:
- `reports_api`: API FastAPI (puerto 8000)
- `reports_db`: PostgreSQL (puerto 5432)

---

## 1) Crear template
- **Método**: `POST`
- **Path**: `/templates/`
- **Tag**: Templates
- **Descripción**: Crea un nuevo template de consulta (nombre, descripción, SQL).
- **Body (JSON)**:
  ```json
  {
    "name": "string (requerido)",
    "description": "string (opcional)",
    "sql_template": "string (requerido)"
  }
  ```
- **Respuesta (200)**:
  ```json
  {
    "message": "Template creado",
    "data": { 
      "id": "uuid",
      "name": "string",
      "description": "string",
      "sql_template": "string",
      "created_at": "timestamp"
    }
  }
  ```
- **Errores**:
  - `500`: Error de SQL / error interno.

**Ejemplo curl**:
```bash
curl -X POST "http://localhost:8000/templates/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Reporte ventas",
    "description": "Reporte mensual de ventas",
    "sql_template": "SELECT * FROM ventas WHERE fecha >= :start_date AND fecha <= :end_date"
  }'
```

---

## 2) Obtener todos los templates
- **Método**: `GET`
- **Path**: `/templates/all`
- **Tag**: Templates
- **Descripción**: Devuelve todos los templates registrados en el sistema.
- **Parámetros**: Ninguno
- **Respuesta (200)**:
  ```json
  {
    "message": "Templates obtenidos",
    "data": [
      {
        "id": "uuid",
        "name": "string",
        "description": "string",
        "sql_template": "string",
        "created_at": "timestamp"
      }
    ]
  }
  ```
- **Errores**:
  - `500`: Error de SQL / error interno.

**Ejemplo curl**:
```bash
curl "http://localhost:8000/templates/all"
```

---

## 3) Obtener ejecuciones
- **Método**: `GET`
- **Path**: `/templates/executions`
- **Tag**: Templates
- **Descripción**: Obtiene todas las ejecuciones o, si se provee `template_id`, las ejecuciones de un template específico. **Incluye información del template mediante JOIN**.
- **Query params**:
  - `template_id` (opcional): UUID del template para filtrar ejecuciones.
- **Respuesta (200)**: Lista de `ExecutionResponse` (JSON array). Cada elemento contiene:
  ```json
  {
    "execution_id": "string (UUID)",
    "template_id": "string (UUID) | null",
    "template_info": {
      "id": "string (UUID)",
      "name": "string",
      "description": "string | null",
      "sql_template": "string"
    } | null,
    "executed_query": "string",
    "parameters": "object | null",
    "status": "string (SUCCESS/FAILED)",
    "row_count": "int | null",
    "error_message": "string | null",
    "executed_at": "string (ISO timestamp)"
  }
  ```
- **Errores**:
  - `400`: Si `template_id` está presente y no es un UUID válido.
  - `500`: Error interno.

**Ejemplo curl (todas las ejecuciones)**:
```bash
curl "http://localhost:8000/templates/executions"
```

**Ejemplo curl (filtrado por template_id)**:
```bash
curl "http://localhost:8000/templates/executions?template_id=7fb78c04-f524-4314-8214-ba126c6ea9eb"
```

---

## 4) Ejecutar un template
- **Método**: `POST`
- **Path**: `/templates/{template_id}/execute`
- **Tag**: Templates
- **Descripción**: Ejecuta el SQL del template indicado con parámetros opcionales y registra la ejecución en `report_executions`.
- **Path params**:
  - `template_id`: UUID del template a ejecutar
- **Body (JSON)**:
  ```json
  {
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    }
  }
  ```
  Por defecto es un objeto vacío `{}`.
  
  **Ejemplo con parámetros**:
  ```json
  {
    "parameters": {
      "start_date": "2025-01-01",
      "end_date": "2025-01-31"
    }
  }
  ```
- **Respuesta (200)**: `ExecuteTemplateResponse`
  ```json
  {
    "execution_id": "string (UUID)",
    "template_id": "string (UUID)",
    "status": "string (SUCCESS/FAILED)",
    "row_count": "int | null",
    "error_message": "string | null"
  }
  ```
- **Errores**:
  - `404`: Template no encontrado.
  - `500`: Error ejecutando template / error interno.

**Ejemplo curl**:
```bash
curl -X POST "http://localhost:8000/templates/7fb78c04-f524-4314-8214-ba126c6ea9eb/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "start_date": "2025-01-01",
      "end_date": "2025-01-31"
    }
  }'
```

---

## 5) Enviar ejecuciones por correo (CSV)
- **Método**: `POST`
- **Path**: `/templates/{template_id}/send_email`
- **Tag**: Templates
- **Descripción**: Recupera las ejecuciones del template especificado y envía un reporte CSV por correo electrónico usando **Resend API**. El CSV incluye información completa del template y todas las ejecuciones relacionadas.
- **Path params**:
  - `template_id`: UUID del template
- **Body (JSON)**:
  ```json
  {
    "to_email": "destinatario@ejemplo.com"
  }
  ```
  **Nota**: El email debe ser válido (validado con Pydantic `EmailStr`).

- **Respuesta (200)**:
  ```json
  {
    "success": true,
    "message": "Correo enviado exitosamente a destinatario@ejemplo.com",
    "executions_count": 5,
    "email_id": "string (Resend email ID)"
  }
  ```

- **Contenido del CSV adjunto**:
  El archivo `report.csv` incluye las siguientes columnas:
  - Execution ID
  - Template ID
  - Template Name
  - Template Description
  - SQL Template
  - Executed Query
  - Parameters
  - Status
  - Row Count
  - Error
  - Executed At

- **Errores**:
  - `404`: No hay ejecuciones para el template solicitado.
  - `500`: Error al enviar correo (verificar `RESEND_API_KEY`) o error interno.

**Ejemplo curl**:
```bash
curl -X POST "http://localhost:8000/templates/7fb78c04-f524-4314-8214-ba126c6ea9eb/send_email" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "usuario@ejemplo.com"
  }'
```

---

## Notas técnicas

### Base de datos
- **Motor**: PostgreSQL con extensión `pgcrypto` para generación de UUIDs
- **Tablas principales**:
  - `query_templates`: Almacena los templates de consultas SQL
  - `report_executions`: Registra cada ejecución de un template
  - `ventas`: Tabla de ejemplo con datos transaccionales

### Relaciones
- `report_executions.template_id` → `query_templates.id` (FK con `ON DELETE SET NULL`)
- Se utiliza SQLAlchemy ORM con `joinedload` para cargar la relación `template` en las ejecuciones

### Servicio de Email
- **Provider**: Resend (https://resend.com)
- **Configuración**: Variable de entorno `RESEND_API_KEY`
- **From address**: `E-commerce Dei <onboarding@resend.dev>` (configurable)
- **Formato**: CSV adjunto en base64
- **Validación**: EmailStr de Pydantic valida el formato del destinatario

### Manejo de errores
- Todos los endpoints usan `HTTPException` para errores consistentes
- Los UUIDs son validados antes de hacer consultas
- Las ejecuciones fallidas se registran con su `error_message`

---

## Ejemplos de flujo completo

### 1. Crear y ejecutar un template
```bash
# 1. Crear template
TEMPLATE_ID=$(curl -s -X POST "http://localhost:8000/templates/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ventas por cliente",
    "description": "Obtiene ventas de un cliente específico",
    "sql_template": "SELECT * FROM ventas WHERE cliente = :cliente"
  }' | jq -r '.data.id')

# 2. Ejecutar template
curl -X POST "http://localhost:8000/templates/${TEMPLATE_ID}/execute" \
  -H "Content-Type: application/json" \
  -d '{"parameters": {"cliente": "Juan"}}'

# 3. Ver ejecuciones
curl "http://localhost:8000/templates/executions?template_id=${TEMPLATE_ID}"

# 4. Enviar reporte por email
curl -X POST "http://localhost:8000/templates/${TEMPLATE_ID}/send_email" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "admin@ejemplo.com"}'
```

---

## Swagger UI
La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

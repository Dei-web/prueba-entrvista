CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE query_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sql_template TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE report_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    template_id UUID REFERENCES query_templates(id) ON DELETE SET NULL,

    executed_query TEXT NOT NULL,
    parameters JSONB,

    status VARCHAR(20) NOT NULL, -- SUCCESS / FAILED
    row_count INT,

    error_message TEXT,
    executed_at TIMESTAMP DEFAULT NOW()
);


CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100),
    producto VARCHAR(100),
    monto NUMERIC(10,2),
    fecha DATE
);

INSERT INTO ventas (cliente, producto, monto, fecha) VALUES
('Juan', 'Laptop', 1200.50, '2025-01-01'),
('Ana', 'Mouse', 25.00, '2025-01-02'),
('Luis', 'Teclado', 75.99, '2025-01-03'),
('María', 'Monitor', 300.00, '2025-01-04'),
('Carlos', 'Laptop', 1100.00, '2025-01-05');

-- -- =========================
-- -- TEMPLATE DE EJEMPLO
-- -- =========================
-- INSERT INTO query_templates (name, description, sql_template)
-- VALUES (
--     'Ventas por fecha',
--     'Consulta ventas desde una fecha dada',
--     'SELECT * FROM ventas WHERE fecha >= :fecha'
-- );

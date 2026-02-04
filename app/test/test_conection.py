import pytest
from sqlalchemy import text


def test_db_connection(db_session):
    """
    Verifica que se puede conectar a la base de datos de pruebas
    y ejecutar una consulta simple.
    """
    try:
        result = db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1
    except Exception as e:
        pytest.fail(f"No se pudo conectar a la DB: {e}")

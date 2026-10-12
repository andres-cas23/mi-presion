"""Configuración común de las pruebas: base de datos temporal y usuario de prueba."""
import os
import tempfile

_tmp = tempfile.mkdtemp()
# Por defecto SQLite temporal; para probar contra PostgreSQL defina TEST_DATABASE_URL
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{_tmp}/pruebas.db")
os.environ["SECRET_KEY"] = "clave-de-pruebas"
os.environ["GEMINI_API_KEY"] = "llave-falsa-para-pruebas"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.sesion import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth(client):
    r = client.post("/auth/registro", json={
        "email": "paciente@ejemplo.co", "password": "ClaveSegura123", "nombre": "María Pérez",
        "fecha_nacimiento": "1958-04-12", "acepta_tratamiento_datos": True})
    assert r.status_code == 201, r.text
    tok = client.post("/auth/token", data={"username": "paciente@ejemplo.co",
                                            "password": "ClaveSegura123"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}

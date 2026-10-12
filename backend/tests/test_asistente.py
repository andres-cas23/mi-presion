"""Pruebas del asistente. Gemini se reemplaza por una función falsa:
así las pruebas no gastan cuota ni necesitan internet."""
import pytest

from app.core.config import Settings
from app.services import asistente_ia


@pytest.fixture()
def gemini_falso(monkeypatch):
    llamadas = []

    def falso(contenidos):
        llamadas.append(contenidos)
        return "Reduzca la sal: evite el cubo de caldo y los embutidos."

    monkeypatch.setattr(asistente_ia, "_llamar_gemini", falso)
    asistente_ia._uso.clear()
    return llamadas


def test_estado_publico(client):
    r = client.get("/asistente/estado").json()
    assert r["configurado"] is True and r["modelo"]


def test_requiere_sesion(client):
    assert client.post("/asistente/preguntar", json={"pregunta": "hola"}).status_code == 401


def test_responde_con_contexto_del_paciente(client, auth, gemini_falso):
    client.post("/lecturas/manual", headers=auth, json={"sistolica": 142, "diastolica": 91})
    r = client.post("/asistente/preguntar", headers=auth, json={"pregunta": "¿Qué debo comer?"})
    assert r.status_code == 200
    assert "sal" in r.json()["respuesta"] and r.json()["urgente"] is False
    enviado = gemini_falso[0]
    assert "142/91" in enviado[0]["texto"]          # el resumen del paciente va primero
    assert enviado[-1]["texto"] == "¿Qué debo comer?"


def test_sin_mis_datos_no_envia_mediciones(client, auth, gemini_falso):
    client.post("/lecturas/manual", headers=auth, json={"sistolica": 142, "diastolica": 91})
    client.post("/asistente/preguntar", headers=auth, json={"pregunta": "¿Qué es la DASH?", "usar_mis_datos": False})
    assert all("142/91" not in c["texto"] for c in gemini_falso[0])


def test_historial_se_envia_con_roles(client, auth, gemini_falso):
    client.post("/asistente/preguntar", headers=auth, json={
        "pregunta": "¿Y el café?", "usar_mis_datos": False,
        "historial": [{"rol": "usuario", "texto": "¿Qué evito?"}, {"rol": "asistente", "texto": "La sal."}]})
    roles = [c["rol"] for c in gemini_falso[0]]
    assert roles == ["user", "model", "user"]


def test_emergencia_agrega_aviso_123(client, auth, gemini_falso):
    r = client.post("/asistente/preguntar", headers=auth,
                    json={"pregunta": "Tengo un dolor en el pecho muy fuerte"}).json()
    assert r["urgente"] is True and "123" in r["respuesta"]


def test_limite_por_hora(client, auth, gemini_falso, monkeypatch):
    monkeypatch.setattr(asistente_ia.settings, "asistente_limite_por_hora", 2)
    for _ in range(2):
        assert client.post("/asistente/preguntar", headers=auth, json={"pregunta": "hola hola"}).status_code == 200
    assert client.post("/asistente/preguntar", headers=auth, json={"pregunta": "hola hola"}).status_code == 429


def test_error_de_cuota_es_amigable(client, auth, monkeypatch):
    asistente_ia._uso.clear()

    def falla(_):
        raise RuntimeError("429 RESOURCE_EXHAUSTED")

    monkeypatch.setattr(asistente_ia, "_llamar_gemini", falla)
    r = client.post("/asistente/preguntar", headers=auth, json={"pregunta": "¿Qué es la presión?"})
    assert r.status_code == 502 and "muchas preguntas" in r.json()["detail"]


def test_sin_llave_responde_503(client, auth, monkeypatch):
    asistente_ia._uso.clear()
    monkeypatch.setattr(asistente_ia.settings, "gemini_api_key", "")
    r = client.post("/asistente/preguntar", headers=auth, json={"pregunta": "hola hola"})
    assert r.status_code == 503


def test_url_de_supabase_se_normaliza():
    s = Settings(database_url="postgresql://postgres.abc:clave@aws-1-us-east-1.pooler.supabase.com:5432/postgres")
    assert s.database_url.startswith("postgresql+psycopg://") and s.es_postgres
    assert Settings(database_url="postgres://u:p@h/db").database_url.startswith("postgresql+psycopg://")

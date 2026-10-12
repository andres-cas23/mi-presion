from datetime import datetime, timedelta

from sqlalchemy import text

from app.db.sesion import engine
from app.services.ble_parser import codificar_medicion
from app.core.tiempo import ahora


def test_registro_exige_consentimiento(client):
    r = client.post("/auth/registro", json={"email": "a@b.co", "password": "12345678x",
                                            "nombre": "Ana", "acepta_tratamiento_datos": False})
    assert r.status_code == 422


def test_rutas_protegidas(client):
    assert client.get("/lecturas").status_code == 401


def test_recordatorios_hbpm_creados_al_registrarse(client, auth):
    recs = client.get("/recordatorios", headers=auth).json()
    assert {r["hora"] for r in recs} == {"07:00", "19:00"}


def test_perfil_y_cifrado_en_reposo(client, auth):
    r = client.put("/perfil", headers=auth, json={
        "sistolica_habitual": 145, "diastolica_habitual": 92,
        "factores_riesgo": ["diabetes", "tabaquismo"], "antecedentes": "Infarto en 2019"})
    assert r.status_code == 200 and r.json()["factores_riesgo"] == ["diabetes", "tabaquismo"]
    with engine.connect() as c:
        crudo = c.execute(text("SELECT antecedentes FROM perfiles_clinicos")).scalar()
    assert "Infarto" not in crudo  # se guarda cifrado


def test_medicamento_crea_recordatorios_y_contexto_inferido(client, auth):
    client.post("/perfil/medicamentos", headers=auth,
                json={"nombre": "Losartán", "dosis": "50 mg", "horarios": ["08:00"]})
    recs = client.get("/recordatorios", headers=auth).json()
    assert any(r["tipo"] == "medicamento" and r["hora"] == "08:00" for r in recs)

    hoy = ahora().replace(hour=7, minute=40, second=0)
    r = client.post("/lecturas/manual", headers=auth,
                    json={"sistolica": 128, "diastolica": 78, "medido_en": hoy.isoformat()})
    lec = r.json()["lectura"]
    assert lec["contexto"] == "antes_medicacion" and lec["contexto_inferido"]
    assert lec["fuente"] == "manual"


def test_crisis_genera_alerta(client, auth):
    r = client.post("/lecturas/manual", headers=auth, json={"sistolica": 186, "diastolica": 112})
    body = r.json()
    assert body["lectura"]["categoria"] == "crisis_hipertensiva"
    assert body["alerta"]["nivel"] == "urgente"
    alertas = client.get("/alertas", headers=auth).json()
    assert len(alertas) == 1
    client.post(f"/alertas/{alertas[0]['id']}/atender", headers=auth)
    assert client.get("/alertas", headers=auth).json() == []


def test_validacion_sistolica_mayor_que_diastolica(client, auth):
    r = client.post("/lecturas/manual", headers=auth, json={"sistolica": 80, "diastolica": 90})
    assert r.status_code == 422


def test_sincronizacion_ble_idempotente(client, auth):
    d = client.post("/dispositivos", headers=auth,
                    json={"fabricante": "Omron", "modelo": "HEM-7155T", "fecha_compra": "2020-01-10"}).json()
    assert d["aviso_calibracion"]  # más de 4 años
    base = ahora() - timedelta(days=1)
    paquetes = [{"payload_hex": codificar_medicion(132, 84, 71, base.replace(hour=7, minute=m)).hex()}
                for m in (0, 2)]
    paquetes.append({"payload_hex": codificar_medicion(128, 80, 69, base.replace(hour=20),
                                                       pulso_irregular=True).hex()})
    paquetes.append({"payload_hex": "0001"})  # corrupto
    r = client.post(f"/dispositivos/{d['id']}/sincronizar-ble", headers=auth, json={"paquetes": paquetes}).json()
    assert (r["nuevas"], r["rechazadas"]) == (3, 1)

    # Re-sincronizar la memoria del tensiómetro no duplica lecturas
    r2 = client.post(f"/dispositivos/{d['id']}/sincronizar-ble", headers=auth,
                     json={"paquetes": paquetes[:3]}).json()
    assert (r2["nuevas"], r2["duplicadas"]) == (0, 3)

    lecturas = client.get("/lecturas", headers=auth).json()
    assert len(lecturas) == 3 and all(l["fuente"] == "bluetooth" for l in lecturas)
    assert any(l["pulso_irregular"] for l in lecturas)
    assert client.get("/dispositivos", headers=auth).json()[0]["ultima_sincronizacion"]


def test_sincronizacion_plataformas_salud(client, auth):
    lote = {"lecturas": [
        {"sistolica": 131, "diastolica": 83, "pulso": 74, "fuente": "google_fit",
         "medido_en": "2026-09-20T07:05:00-05:00", "id_externo": "gfit-001"},
        {"sistolica": 190, "diastolica": 100, "fuente": "samsung_health",
         "medido_en": "2026-09-20T20:05:00Z", "id_externo": "sh-001"},
    ]}
    r = client.post("/lecturas/sincronizar", headers=auth, json=lote).json()
    assert r["nuevas"] == 2 and len(r["alertas"]) == 1
    r = client.post("/lecturas/sincronizar", headers=auth, json=lote).json()
    assert r["duplicadas"] == 2
    lecturas = client.get("/lecturas", headers=auth).json()
    # 20:05 UTC -> 15:05 hora de Bogotá
    assert any(l["medido_en"] == "2026-09-20T15:05:00" for l in lecturas)


def test_hbpm_tendencias_y_reportes(client, auth):
    hoy = ahora().replace(second=0)
    lote = []
    for d in range(7):
        dia = hoy - timedelta(days=d)
        for h in (7, 20):
            for k in range(2):
                lote.append({"sistolica": 138, "diastolica": 86, "pulso": 72, "fuente": "apple_health",
                             "medido_en": dia.replace(hour=h, minute=k * 2).isoformat(),
                             "id_externo": f"ah-{d}-{h}-{k}"})
    client.post("/lecturas/sincronizar", headers=auth, json={"lecturas": lote})

    h = client.get("/lecturas/hbpm", headers=auth).json()
    assert h["protocolo_ideal_cumplido"] and h["supera_umbral_domiciliario"]

    t = client.get("/lecturas/tendencias?agrupacion=semana", headers=auth).json()
    assert sum(g["n"] for g in t) == 28

    csv = client.get("/reportes/csv", headers=auth)
    assert csv.status_code == 200 and csv.text.count("\n") == 29
    pdf = client.get("/reportes/pdf", headers=auth)
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    fhir = client.get("/reportes/fhir", headers=auth).json()
    assert fhir["resourceType"] == "Bundle" and len(fhir["entry"]) == 28


def test_educacion_publica(client):
    items = client.get("/educacion").json()
    assert any(i["slug"] == "dieta-dash-colombiana" for i in items)
    assert "cubo" in " ".join(client.get("/educacion/dieta-dash-colombiana").json()["secciones"])


def test_exportar_y_eliminar_cuenta(client, auth):
    client.post("/lecturas/manual", headers=auth, json={"sistolica": 186, "diastolica": 112})
    datos = client.get("/privacidad/exportar", headers=auth).json()
    assert len(datos["lecturas"]) == 1 and len(datos["alertas"]) == 1
    assert client.delete("/privacidad/cuenta", headers=auth).status_code == 204
    assert client.get("/perfil", headers=auth).status_code == 401
    with engine.connect() as c:
        for tabla in ("lecturas", "alertas", "recordatorios", "perfiles_clinicos"):
            assert c.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar() == 0

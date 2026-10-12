"""Simulador de tensiómetro Bluetooth para demostraciones y pruebas.

Genera una semana de mediciones siguiendo el protocolo HBPM (2 tomas en la
mañana y 2 en la noche), las codifica como paquetes GATT 0x2A35 reales y las
envía a la API como lo haría la app móvil.

Uso (desde la carpeta backend/, con la API encendida):
    python -m scripts.simulador_tensiometro --crisis

Contra la API publicada en Render:
    python -m scripts.simulador_tensiometro --api https://SU-API.onrender.com --crisis
"""
import argparse
import random
from datetime import datetime, timedelta

import httpx

from app.services.ble_parser import codificar_medicion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--email", default="demo@ejemplo.co")
    ap.add_argument("--password", default="Demo12345")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--sistolica-media", type=int, default=138)
    ap.add_argument("--crisis", action="store_true", help="Incluye una lectura >= 180/120")
    a = ap.parse_args()

    with httpx.Client(base_url=a.api, timeout=30) as c:
        c.post("/auth/registro", json={"email": a.email, "password": a.password, "nombre": "Paciente Demo",
                                       "fecha_nacimiento": "1956-03-02", "acepta_tratamiento_datos": True})
        tok = c.post("/auth/token", data={"username": a.email, "password": a.password})
        tok.raise_for_status()
        c.headers["Authorization"] = f"Bearer {tok.json()['access_token']}"

        disp = c.post("/dispositivos", json={"fabricante": "Omron", "modelo": "HEM-7155T (simulado)",
                                             "direccion_ble": "AA:BB:CC:DD:EE:01"}).json()
        hoy = datetime.now().replace(second=0, microsecond=0)
        paquetes = []
        for d in range(a.dias - 1, -1, -1):
            dia = hoy - timedelta(days=d)
            for hora in (7, 20):
                base = dia.replace(hour=hora, minute=random.randint(0, 20))
                if base + timedelta(minutes=2) > hoy:
                    continue  # no generar mediciones en el futuro
                for k in range(2):
                    sis = random.gauss(a.sistolica_media - (d * 0.6), 5)
                    dia_ = sis * 0.62 + random.gauss(0, 3)
                    paquetes.append(codificar_medicion(
                        round(sis), round(dia_), round(random.gauss(72, 5)),
                        base + timedelta(minutes=2 * k), pulso_irregular=random.random() < 0.03).hex())
        if a.crisis:
            paquetes.append(codificar_medicion(186, 118, 88, hoy - timedelta(hours=1)).hex())

        r = c.post(f"/dispositivos/{disp['id']}/sincronizar-ble",
                   json={"paquetes": [{"payload_hex": p} for p in paquetes]}).json()
        print(f"Sincronización: {r['nuevas']} nuevas, {r['duplicadas']} duplicadas, "
              f"{r['rechazadas']} rechazadas, {len(r['alertas'])} alertas")
        h = c.get("/lecturas/hbpm").json()
        print(f"Promedio HBPM: {h['promedio_sistolica']}/{h['promedio_diastolica']} — {h['interpretacion']}")
        with open("informe_demo.pdf", "wb") as f:
            f.write(c.get("/reportes/pdf").content)
        print("Informe guardado en informe_demo.pdf")
        print(f"Abra el frontend en el navegador y entre con {a.email} / {a.password}")


if __name__ == "__main__":
    main()

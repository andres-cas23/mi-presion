"""Puente Bluetooth real: lee un tensiómetro BLE y envía las lecturas a la API.

Sirve para probar la integración con hardware desde un PC (Windows, macOS o
Linux) mientras se construye la app móvil; en la app, la misma lógica se
implementa con flutter_blue_plus o react-native-ble-plx.

Requisitos: pip install bleak httpx
Uso:
    python -m scripts.puente_ble --escanear
    python -m scripts.puente_ble --direccion AA:BB:CC:DD:EE:FF --dispositivo-id 1 \
        --email paciente@correo.co --password ********

Notas:
 - Muchos tensiómetros solo son visibles unos segundos después de medir o al
   presionar el botón de sincronización/Bluetooth.
 - Varios equipos (p. ej. Omron) exigen emparejamiento previo y envían las
   lecturas guardadas en memoria como indicaciones al suscribirse.
 - Algunas marcas usan servicios propietarios además del estándar 0x1810;
   este puente cubre el perfil estándar del Bluetooth SIG.
"""
import argparse
import asyncio
from datetime import datetime

import httpx
from bleak import BleakClient, BleakScanner

from app.services.ble_parser import UUID_MEDICION_PRESION, UUID_SERVICIO_PRESION, decodificar_medicion


async def escanear():
    print("Buscando tensiómetros (servicio 0x1810) durante 10 s...")
    encontrados = await BleakScanner.discover(timeout=10, return_adv=True)
    for disp, adv in encontrados.values():
        if UUID_SERVICIO_PRESION in [u.lower() for u in adv.service_uuids]:
            print(f"  {disp.address}  {disp.name or '(sin nombre)'}  RSSI={adv.rssi}")


async def leer(direccion: str, espera: int) -> list[dict]:
    paquetes: list[dict] = []

    def al_recibir(_, datos: bytearray):
        m = decodificar_medicion(bytes(datos))
        print(f"  Lectura: {m.sistolica:.0f}/{m.diastolica:.0f} mmHg, pulso {m.pulso}, {m.marca_tiempo}")
        paquetes.append({"payload_hex": bytes(datos).hex(), "recibido_en": datetime.now().isoformat()})

    async with BleakClient(direccion) as cli:
        print(f"Conectado a {direccion}. Esperando lecturas {espera} s...")
        await cli.start_notify(UUID_MEDICION_PRESION, al_recibir)
        await asyncio.sleep(espera)
        await cli.stop_notify(UUID_MEDICION_PRESION)
    return paquetes


def enviar(api: str, email: str, password: str, dispositivo_id: int, paquetes: list[dict]):
    with httpx.Client(base_url=api, timeout=30) as c:
        tok = c.post("/auth/token", data={"username": email, "password": password})
        tok.raise_for_status()
        r = c.post(f"/dispositivos/{dispositivo_id}/sincronizar-ble",
                   headers={"Authorization": f"Bearer {tok.json()['access_token']}"},
                   json={"paquetes": paquetes})
        r.raise_for_status()
        print("Respuesta de la API:", r.json())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--escanear", action="store_true")
    ap.add_argument("--direccion")
    ap.add_argument("--dispositivo-id", type=int)
    ap.add_argument("--espera", type=int, default=30)
    ap.add_argument("--api", default="http://127.0.0.1:8000")
    ap.add_argument("--email")
    ap.add_argument("--password")
    a = ap.parse_args()

    if a.escanear:
        asyncio.run(escanear())
        return
    if not (a.direccion and a.dispositivo_id and a.email and a.password):
        ap.error("Indique --direccion, --dispositivo-id, --email y --password (o use --escanear)")
    paquetes = asyncio.run(leer(a.direccion, a.espera))
    if paquetes:
        enviar(a.api, a.email, a.password, a.dispositivo_id, paquetes)
    else:
        print("No se recibieron lecturas.")


if __name__ == "__main__":
    main()

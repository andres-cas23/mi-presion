"""Decodificador del perfil Bluetooth estándar de presión arterial (RF-02).

Servicio GATT 0x1810 (Blood Pressure), característica 0x2A35
(Blood Pressure Measurement). Los tensiómetros validados con Bluetooth
(Omron, Withings, A&D, Beurer, etc.) exponen este perfil estándar del
Bluetooth SIG, por lo que un único decodificador sirve para varias marcas.

Formato del paquete:
  byte 0      flags
                bit0: unidades (0 = mmHg, 1 = kPa)
                bit1: incluye marca de tiempo
                bit2: incluye pulso
                bit3: incluye ID de usuario
                bit4: incluye estado de la medición
  bytes 1-6   sistólica, diastólica, presión arterial media (SFLOAT IEEE-11073)
  [7 bytes]   marca de tiempo: año(uint16), mes, día, hora, minuto, segundo
  [2 bytes]   pulso (SFLOAT)
  [1 byte]    ID de usuario del tensiómetro
  [2 bytes]   estado (bit0 movimiento, bit1 brazalete flojo, bit2 pulso irregular,
              bits3-4 rango de pulso, bit5 posición incorrecta)
"""
import struct
from dataclasses import dataclass
from datetime import datetime

KPA_A_MMHG = 7.50062

UUID_SERVICIO_PRESION = "00001810-0000-1000-8000-00805f9b34fb"
UUID_MEDICION_PRESION = "00002a35-0000-1000-8000-00805f9b34fb"


class ErrorPaqueteBLE(ValueError):
    pass


@dataclass
class MedicionBLE:
    sistolica: float
    diastolica: float
    presion_arterial_media: float | None
    pulso: float | None
    marca_tiempo: datetime | None
    id_usuario_dispositivo: int | None
    movimiento_detectado: bool = False
    brazalete_flojo: bool = False
    pulso_irregular: bool = False
    posicion_incorrecta: bool = False
    unidad_original: str = "mmHg"


def sfloat_a_float(raw: int) -> float | None:
    """Convierte un SFLOAT IEEE-11073 de 16 bits (exponente 4 bits, mantisa 12 bits)."""
    if raw in (0x07FF, 0x0800, 0x07FE, 0x0802, 0x0801):  # NaN, NRes, +INF, -INF, reservado
        return None
    mantisa = raw & 0x0FFF
    exponente = (raw >> 12) & 0x0F
    if mantisa >= 0x0800:
        mantisa -= 0x1000
    if exponente >= 0x08:
        exponente -= 0x10
    return mantisa * (10 ** exponente)


def float_a_sfloat(valor: float) -> int:
    """Inverso de sfloat_a_float (útil para simuladores y pruebas)."""
    exponente = 0
    while valor != int(valor) and exponente > -8:
        valor *= 10
        exponente -= 1
    mantisa = int(round(valor))
    return ((exponente & 0x0F) << 12) | (mantisa & 0x0FFF)


def decodificar_medicion(datos: bytes) -> MedicionBLE:
    if len(datos) < 7:
        raise ErrorPaqueteBLE("Paquete demasiado corto")
    flags = datos[0]
    kpa = bool(flags & 0x01)
    pos = 1

    def leer_sfloat() -> float | None:
        nonlocal pos
        if pos + 2 > len(datos):
            raise ErrorPaqueteBLE("Paquete truncado")
        (raw,) = struct.unpack_from("<H", datos, pos)
        pos += 2
        return sfloat_a_float(raw)

    sis, dia, pam = leer_sfloat(), leer_sfloat(), leer_sfloat()
    if sis is None or dia is None:
        raise ErrorPaqueteBLE("El dispositivo reportó una medición inválida")

    marca = None
    if flags & 0x02:
        if pos + 7 > len(datos):
            raise ErrorPaqueteBLE("Marca de tiempo truncada")
        anio, mes, d, h, mi, s = struct.unpack_from("<HBBBBB", datos, pos)
        pos += 7
        try:
            marca = datetime(anio, mes, d, h, mi, s)
        except ValueError:
            marca = None  # el dispositivo no tiene reloj configurado

    pulso = leer_sfloat() if flags & 0x04 else None

    id_usuario = None
    if flags & 0x08:
        if pos + 1 > len(datos):
            raise ErrorPaqueteBLE("ID de usuario truncado")
        id_usuario = datos[pos]
        pos += 1
        if id_usuario == 0xFF:  # usuario desconocido
            id_usuario = None

    estado = 0
    if flags & 0x10:
        if pos + 2 > len(datos):
            raise ErrorPaqueteBLE("Estado truncado")
        (estado,) = struct.unpack_from("<H", datos, pos)

    if kpa:
        sis, dia = sis * KPA_A_MMHG, dia * KPA_A_MMHG
        pam = pam * KPA_A_MMHG if pam is not None else None

    return MedicionBLE(
        sistolica=round(sis, 1), diastolica=round(dia, 1),
        presion_arterial_media=round(pam, 1) if pam is not None else None,
        pulso=pulso, marca_tiempo=marca, id_usuario_dispositivo=id_usuario,
        movimiento_detectado=bool(estado & 0x01), brazalete_flojo=bool(estado & 0x02),
        pulso_irregular=bool(estado & 0x04), posicion_incorrecta=bool(estado & 0x20),
        unidad_original="kPa" if kpa else "mmHg",
    )


def codificar_medicion(sistolica: float, diastolica: float, pulso: float | None = None,
                       marca_tiempo: datetime | None = None, pulso_irregular: bool = False,
                       id_usuario: int | None = None) -> bytes:
    """Genera un paquete 0x2A35 válido en mmHg (para simulación y pruebas)."""
    flags = 0x10
    pam = round(diastolica + (sistolica - diastolica) / 3)
    cuerpo = struct.pack("<HHH", float_a_sfloat(sistolica), float_a_sfloat(diastolica), float_a_sfloat(pam))
    if marca_tiempo:
        flags |= 0x02
        cuerpo += struct.pack("<HBBBBB", marca_tiempo.year, marca_tiempo.month, marca_tiempo.day,
                              marca_tiempo.hour, marca_tiempo.minute, marca_tiempo.second)
    if pulso is not None:
        flags |= 0x04
        cuerpo += struct.pack("<H", float_a_sfloat(pulso))
    if id_usuario is not None:
        flags |= 0x08
        cuerpo += struct.pack("<B", id_usuario)
    cuerpo += struct.pack("<H", 0x04 if pulso_irregular else 0)
    return bytes([flags]) + cuerpo

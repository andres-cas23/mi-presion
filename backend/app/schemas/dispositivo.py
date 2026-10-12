"""Dispositivos y paquetes Bluetooth."""
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import Contexto, TipoDispositivo
from app.schemas.comun import DesdeModelo


class DispositivoEntrada(BaseModel):
    tipo: TipoDispositivo = TipoDispositivo.TENSIOMETRO_BLE
    fabricante: str = Field(min_length=1, max_length=60, examples=["Omron"])
    modelo: str = Field(min_length=1, max_length=80, examples=["HEM-7155T"])
    direccion_ble: str | None = None
    fecha_compra: date | None = None


class DispositivoSalida(DesdeModelo):
    id: int
    tipo: str
    fabricante: str
    modelo: str
    direccion_ble: str | None
    fecha_compra: date | None
    ultima_sincronizacion: datetime | None
    aviso_calibracion: str | None = None


class PaqueteBLE(BaseModel):
    """Bytes crudos de la característica Bluetooth 0x2A35, tal como los envía el tensiómetro."""
    payload_hex: str = Field(max_length=200, examples=["1e7a0050005d00ea07090f0800000048000100"])
    recibido_en: datetime | None = None
    contexto: Contexto | None = None


class SincronizacionBLE(BaseModel):
    paquetes: list[PaqueteBLE] = Field(min_length=1, max_length=500)

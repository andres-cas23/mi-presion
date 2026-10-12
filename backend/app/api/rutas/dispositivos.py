"""/dispositivos: tensiómetros y sincronización Bluetooth (RF-02)."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencias import obtener_propio, usuario_actual
from app.core.tiempo import a_hora_local
from app.db.sesion import obtener_db
from app.models import Dispositivo, Usuario
from app.models.enums import Fuente
from app.schemas import (AlertaSalida, DispositivoEntrada, DispositivoSalida, LecturaEntrada,
                         ResultadoSincronizacion, SincronizacionBLE)
from app.services.ble_parser import ErrorPaqueteBLE, decodificar_medicion
from app.services.lecturas import registrar_lectura

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])


def _salida(d: Dispositivo) -> DispositivoSalida:
    s = DispositivoSalida.model_validate(d)
    if d.fecha_compra and (date.today() - d.fecha_compra).days > 4 * 365:
        s.aviso_calibracion = ("Su tensiómetro tiene más de 4 años y puede haber perdido precisión. "
                               "Hágalo revisar o considere cambiarlo.")
    return s


@router.get("", response_model=list[DispositivoSalida])
def listar(u: Usuario = Depends(usuario_actual)):
    return [_salida(d) for d in u.dispositivos]


@router.post("", response_model=DispositivoSalida, status_code=201)
def vincular(datos: DispositivoEntrada, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    d = Dispositivo(usuario_id=u.id, tipo=datos.tipo.value, fabricante=datos.fabricante, modelo=datos.modelo,
                    direccion_ble=datos.direccion_ble, fecha_compra=datos.fecha_compra)
    db.add(d)
    db.commit()
    return _salida(d)


@router.delete("/{disp_id}", status_code=204)
def desvincular(disp_id: int, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    db.delete(obtener_propio(db, Dispositivo, disp_id, u, "Dispositivo"))
    db.commit()


@router.post("/{disp_id}/sincronizar-ble", response_model=ResultadoSincronizacion)
def sincronizar_ble(disp_id: int, datos: SincronizacionBLE, u: Usuario = Depends(usuario_actual),
                    db: Session = Depends(obtener_db)):
    """Recibe los bytes crudos que la app leyó del tensiómetro por Bluetooth,
    los decodifica y los guarda (incluye las mediciones guardadas en su memoria)."""
    d = obtener_propio(db, Dispositivo, disp_id, u, "Dispositivo")
    res = ResultadoSincronizacion(recibidas=len(datos.paquetes))
    for i, p in enumerate(datos.paquetes):
        try:
            m = decodificar_medicion(bytes.fromhex(p.payload_hex))
            medido_en = m.marca_tiempo or (a_hora_local(p.recibido_en) if p.recibido_en else None)
            clave = medido_en.isoformat() if medido_en else p.payload_hex
            entrada = LecturaEntrada(
                sistolica=round(m.sistolica), diastolica=round(m.diastolica),
                pulso=round(m.pulso) if m.pulso else None, medido_en=medido_en, contexto=p.contexto,
                id_externo=f"ble:{d.id}:{clave}:{round(m.sistolica)}/{round(m.diastolica)}")
        except (ValueError, ErrorPaqueteBLE) as e:
            res.rechazadas += 1
            res.errores.append(f"Paquete {i}: {e}")
            continue
        r = registrar_lectura(db, u, entrada, Fuente.BLUETOOTH, dispositivo=d, pam=m.presion_arterial_media,
                              pulso_irregular=m.pulso_irregular, movimiento=m.movimiento_detectado, commit=False)
        if r.duplicada:
            res.duplicadas += 1
        else:
            res.nuevas += 1
            if r.alerta:
                db.flush()
                res.alertas.append(AlertaSalida.model_validate(r.alerta))
    db.commit()
    return res

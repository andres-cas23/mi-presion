from datetime import datetime

import pytest

from app.services.ble_parser import (ErrorPaqueteBLE, codificar_medicion, decodificar_medicion,
                                     sfloat_a_float)


def test_sfloat():
    assert sfloat_a_float(0x0078) == 120        # 120 * 10^0
    assert sfloat_a_float(0xF4B0) == pytest.approx(120.0)  # 1200 * 10^-1
    assert sfloat_a_float(0x07FF) is None       # NaN


def test_paquete_minimo_mmhg():
    # flags=0, 120/80, PAM 93
    datos = bytes.fromhex("00" "7800" "5000" "5d00")
    m = decodificar_medicion(datos)
    assert (m.sistolica, m.diastolica, m.presion_arterial_media) == (120, 80, 93)
    assert m.marca_tiempo is None and m.pulso is None


def test_paquete_completo_con_tiempo_pulso_usuario_estado():
    # flags=0x1E: tiempo + pulso + usuario + estado. 2026-09-15 08:00:00, pulso 72, usuario 1, pulso irregular
    datos = bytes.fromhex("1e" "7a00" "5000" "5d00" "ea07" "09" "0f" "08" "00" "00" "4800" "01" "0400")
    m = decodificar_medicion(datos)
    assert m.sistolica == 122 and m.diastolica == 80
    assert m.marca_tiempo == datetime(2026, 9, 15, 8, 0, 0)
    assert m.pulso == 72 and m.id_usuario_dispositivo == 1
    assert m.pulso_irregular and not m.movimiento_detectado


def test_kpa_se_convierte_a_mmhg():
    # flags=1 (kPa): 16.0 kPa (160 * 10^-1 = 0xF0A0) / 10.7 kPa (107 * 10^-1 = 0xF06B)
    datos = bytes.fromhex("01" "a0f0" "6bf0" "ffff")
    m = decodificar_medicion(datos)
    assert m.unidad_original == "kPa"
    assert m.sistolica == pytest.approx(120.0, abs=0.1)
    assert m.diastolica == pytest.approx(80.3, abs=0.1)


def test_ida_y_vuelta_codificador():
    t = datetime(2026, 9, 20, 19, 30, 5)
    m = decodificar_medicion(codificar_medicion(138, 88, 70, t, pulso_irregular=True, id_usuario=2))
    assert (m.sistolica, m.diastolica, m.pulso, m.marca_tiempo) == (138, 88, 70, t)
    assert m.pulso_irregular and m.id_usuario_dispositivo == 2


def test_paquete_truncado():
    with pytest.raises(ErrorPaqueteBLE):
        decodificar_medicion(bytes.fromhex("067800"))

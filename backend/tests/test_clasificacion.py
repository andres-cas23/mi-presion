import pytest

from app.models.enums import Categoria, NivelAlerta
from app.services.clasificacion import clasificar, en_meta


@pytest.mark.parametrize("sis,dia,esperada", [
    (115, 65, Categoria.NO_ELEVADA),
    (119, 69, Categoria.NO_ELEVADA),
    (120, 65, Categoria.ELEVADA),
    (115, 70, Categoria.ELEVADA),
    (139, 89, Categoria.ELEVADA),
    (140, 80, Categoria.HIPERTENSION),
    (130, 90, Categoria.HIPERTENSION),
    (179, 119, Categoria.HIPERTENSION),
    (180, 100, Categoria.CRISIS),
    (160, 120, Categoria.CRISIS),
])
def test_categorias_esc_2024(sis, dia, esperada):
    assert clasificar(sis, dia).categoria == esperada


def test_crisis_genera_alerta_urgente_con_linea_123():
    r = clasificar(185, 115)
    assert r.nivel_alerta == NivelAlerta.URGENTE
    assert "123" in r.mensaje


def test_hipotension_genera_advertencia():
    r = clasificar(85, 55)
    assert r.nivel_alerta == NivelAlerta.ADVERTENCIA


def test_sin_alerta_en_rango_normal():
    assert clasificar(125, 78).nivel_alerta is None


def test_meta_personal():
    assert en_meta(125, 78)
    assert not en_meta(132, 78)
    assert en_meta(132, 78, meta_sis_max=135)

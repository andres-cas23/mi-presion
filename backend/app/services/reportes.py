"""Exportación de informes para el médico tratante (RF-07) e interoperabilidad
HL7 FHIR R4 (RNF de interoperabilidad)."""
import csv
import io
from datetime import datetime

from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Lectura, Usuario
from app.services.hbpm import ResumenHBPM
from app.core.tiempo import ahora

NOMBRES_CATEGORIA = {
    "no_elevada": "No elevada",
    "elevada": "Elevada",
    "hipertension": "Hipertensión",
    "crisis_hipertensiva": "Crisis (≥180/120)",
}
NOMBRES_FUENTE = {"bluetooth": "Bluetooth", "manual": "Manual", "apple_health": "Apple Health",
                  "google_fit": "Google Fit", "samsung_health": "Samsung Health"}

COLUMNAS_CSV = ["fecha_hora", "sistolica", "diastolica", "pulso", "categoria", "contexto",
                "fuente", "pulso_irregular", "en_meta", "notas"]


def generar_csv(lecturas: list[Lectura]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(COLUMNAS_CSV)
    for l in lecturas:
        w.writerow([l.medido_en.isoformat(sep=" "), l.sistolica, l.diastolica, l.pulso or "",
                    l.categoria, l.contexto, l.fuente, "si" if l.pulso_irregular else "no",
                    "si" if l.en_meta else "no", l.notas or ""])
    return "\ufeff" + buf.getvalue()  # BOM para que Excel en español abra bien las tildes


def _grafico(lecturas: list[Lectura]) -> Drawing:
    d = Drawing(17 * cm, 6.5 * cm)
    if len(lecturas) < 2:
        d.add(String(10, 80, "No hay suficientes lecturas para graficar.", fontSize=10, fontName="Helvetica"))
        return d
    base = lecturas[0].medido_en
    x = lambda l: (l.medido_en - base).total_seconds() / 86400  # días desde el inicio
    lp = LinePlot()
    lp.x, lp.y, lp.width, lp.height = 40, 25, 16 * cm - 40, 5.5 * cm - 25
    lp.data = [[(x(l), l.sistolica) for l in lecturas], [(x(l), l.diastolica) for l in lecturas],
               [(0, 135), (x(lecturas[-1]), 135)], [(0, 85), (x(lecturas[-1]), 85)]]
    estilos = [(colors.HexColor("#1f5fa8"), True), (colors.HexColor("#2e8b57"), True),
               (colors.HexColor("#c0392b"), False), (colors.HexColor("#e67e22"), False)]
    for i, (c, marcador) in enumerate(estilos):
        lp.lines[i].strokeColor = c
        lp.lines[i].strokeWidth = 1.5 if marcador else 0.8
        if marcador:
            lp.lines[i].symbol = makeMarker("FilledCircle", size=3)
        else:
            lp.lines[i].strokeDashArray = [3, 3]
    lp.yValueAxis.valueMin = 40
    lp.yValueAxis.valueMax = max(200, max(l.sistolica for l in lecturas) + 10)
    lp.xValueAxis.labelTextFormat = lambda v: f"día {int(v) + 1}"
    d.add(lp)
    d.add(String(45, 6.2 * cm - 8, "— Sistólica (azul)  — Diastólica (verde)  - - Umbral domiciliario 135/85",
                 fontSize=7.5, fontName="Helvetica", fillColor=colors.grey))
    return d


def generar_pdf(usuario: Usuario, lecturas: list[Lectura], resumen: ResumenHBPM,
                desde: datetime | None, hasta: datetime | None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Informe de presión arterial")
    est = getSampleStyleSheet()
    normal = ParagraphStyle("n", parent=est["Normal"], fontSize=10.5, leading=14)
    el = [Paragraph("Informe de presión arterial", est["Title"])]

    periodo = (f"{desde:%d/%m/%Y}" if desde else "inicio") + " a " + (f"{hasta:%d/%m/%Y}" if hasta else "hoy")
    edad = ""
    if usuario.fecha_nacimiento:
        hoy = ahora().date()
        fn = usuario.fecha_nacimiento
        edad = f" · {hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))} años"
    el.append(Paragraph(f"<b>Paciente:</b> {usuario.nombre}{edad}<br/><b>Periodo:</b> {periodo}"
                        f"<br/><b>Generado:</b> {ahora():%d/%m/%Y %H:%M}", normal))
    perfil = usuario.perfil
    if perfil:
        el.append(Paragraph(f"<b>Meta terapéutica:</b> sistólica {perfil.meta_sistolica_min}-"
                            f"{perfil.meta_sistolica_max} mmHg, diastólica ≤ {perfil.meta_diastolica_max} mmHg", normal))
    el.append(Spacer(1, 10))

    el.append(Paragraph("Resumen del monitoreo domiciliario (últimos 7 días)", est["Heading2"]))
    datos_res = [
        ["Promedio", f"{resumen.promedio_sistolica or '-'} / {resumen.promedio_diastolica or '-'} mmHg"],
        ["Pulso promedio", f"{resumen.promedio_pulso or '-'} lpm"],
        ["Lecturas / días con lecturas", f"{resumen.total_lecturas} / {resumen.dias_con_lecturas}"],
        ["Días completos (mañana y noche)", str(resumen.dias_completos)],
        ["Protocolo mínimo (3 días)", "Cumplido" if resumen.protocolo_minimo_cumplido else "No cumplido"],
    ]
    t = Table(datos_res, colWidths=[7 * cm, 9 * cm])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 10),
                           ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4fb")),
                           ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b0c4de"))]))
    el += [t, Spacer(1, 6), Paragraph(resumen.interpretacion, normal), Spacer(1, 10)]

    el.append(Paragraph("Tendencia", est["Heading2"]))
    el.append(_grafico(lecturas))

    el.append(Paragraph("Detalle de lecturas", est["Heading2"]))
    filas = [["Fecha y hora", "PAS", "PAD", "Pulso", "Categoría", "Fuente", "Obs."]]
    for l in lecturas:
        obs = "Pulso irregular" if l.pulso_irregular else ""
        filas.append([f"{l.medido_en:%d/%m/%Y %H:%M}", l.sistolica, l.diastolica, l.pulso or "-",
                      NOMBRES_CATEGORIA.get(l.categoria, l.categoria),
                      NOMBRES_FUENTE.get(l.fuente, l.fuente), obs])
    tabla = Table(filas, repeatRows=1,
                  colWidths=[3.4 * cm, 1.3 * cm, 1.3 * cm, 1.3 * cm, 3.3 * cm, 2.6 * cm, 2.8 * cm])
    estilo = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f5fa8")),
              ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
              ("FONTSIZE", (0, 0), (-1, -1), 8.5),
              ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
              ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f9fc")])]
    for i, l in enumerate(lecturas, start=1):
        if l.categoria == "crisis_hipertensiva":
            estilo.append(("TEXTCOLOR", (0, i), (-1, i), colors.HexColor("#b03a2e")))
    tabla.setStyle(TableStyle(estilo))
    el.append(tabla)
    el += [Spacer(1, 10), Paragraph(
        "<i>Informe generado automáticamente a partir de mediciones domiciliarias. "
        "No reemplaza la valoración médica.</i>", ParagraphStyle("p", parent=normal, fontSize=8.5))]
    doc.build(el)
    return buf.getvalue()


def generar_bundle_fhir(usuario: Usuario, lecturas: list[Lectura]) -> dict:
    """Bundle FHIR R4 con Observations de presión arterial (perfil vital-signs, LOINC 85354-9)."""
    entradas = []
    for l in lecturas:
        componentes = [
            {"code": {"coding": [{"system": "http://loinc.org", "code": "8480-6",
                                  "display": "Systolic blood pressure"}]},
             "valueQuantity": {"value": l.sistolica, "unit": "mmHg",
                               "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}},
            {"code": {"coding": [{"system": "http://loinc.org", "code": "8462-4",
                                  "display": "Diastolic blood pressure"}]},
             "valueQuantity": {"value": l.diastolica, "unit": "mmHg",
                               "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}},
        ]
        if l.pulso:
            componentes.append({"code": {"coding": [{"system": "http://loinc.org", "code": "8867-4",
                                                      "display": "Heart rate"}]},
                                "valueQuantity": {"value": l.pulso, "unit": "/min",
                                                  "system": "http://unitsofmeasure.org", "code": "/min"}})
        entradas.append({"resource": {
            "resourceType": "Observation",
            "id": f"bp-{l.id}",
            "status": "final",
            "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                      "code": "vital-signs"}]}],
            "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9",
                                 "display": "Blood pressure panel with all children optional"}]},
            "subject": {"reference": f"Patient/{usuario.id}", "display": usuario.nombre},
            "effectiveDateTime": l.medido_en.isoformat(),
            "component": componentes,
            "note": [{"text": f"Fuente: {l.fuente}; contexto: {l.contexto}"}],
        }})
    return {"resourceType": "Bundle", "type": "collection",
            "timestamp": datetime.now().astimezone().isoformat(), "entry": entradas}

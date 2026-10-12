"""/asistente: preguntas sobre hipertensión respondidas con Gemini."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencias import usuario_actual
from app.core.config import settings
from app.core.tiempo import ahora
from app.db.sesion import obtener_db
from app.models import Usuario
from app.schemas import EstadoAsistente, Pregunta, Respuesta
from app.services import asistente_ia
from app.services.hbpm import resumen_hbpm
from app.services.lecturas import consultar_lecturas

router = APIRouter(prefix="/asistente", tags=["Asistente IA"])


@router.get("/estado", response_model=EstadoAsistente)
def estado():
    return EstadoAsistente(configurado=bool(settings.gemini_api_key), modelo=settings.gemini_modelo,
                           limite_por_hora=settings.asistente_limite_por_hora)


@router.post("/preguntar", response_model=Respuesta)
def preguntar(datos: Pregunta, u: Usuario = Depends(usuario_actual), db: Session = Depends(obtener_db)):
    try:
        asistente_ia.verificar_limite(u.id)
    except asistente_ia.LimiteExcedido:
        raise HTTPException(429, f"Ha hecho muchas preguntas en la última hora "
                                 f"(máximo {settings.asistente_limite_por_hora}). Intente más tarde.")

    contexto = None
    if datos.usar_mis_datos:
        lecturas = consultar_lecturas(db, u.id)
        resumen = resumen_hbpm(lecturas, hasta=ahora().date())
        meta = (u.perfil.meta_sistolica_max, u.perfil.meta_diastolica_max) if u.perfil else None
        contexto = asistente_ia.construir_contexto_paciente(u.nombre, resumen, lecturas[-1] if lecturas else None, meta)

    try:
        texto, urgente = asistente_ia.responder(datos.pregunta, datos.historial, contexto)
    except asistente_ia.AsistenteNoConfigurado:
        raise HTTPException(503, "El asistente aún no está activado: falta configurar GEMINI_API_KEY en el servidor.")
    except asistente_ia.ErrorAsistente as e:
        raise HTTPException(502, str(e))
    return Respuesta(respuesta=texto, urgente=urgente, modelo=settings.gemini_modelo)

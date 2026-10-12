"""ESQUEMAS = la forma de los datos que entran y salen de la API
(equivale a forms.py / serializers.py en Django).

Revisan que los datos tengan sentido ANTES de tocar la base de datos.
Ejemplo: rechazan una presión de 500 o un correo sin @.
"""
from app.schemas.asistente import EstadoAsistente, MensajeChat, Pregunta, Respuesta
from app.schemas.dispositivo import DispositivoEntrada, DispositivoSalida, PaqueteBLE, SincronizacionBLE
from app.schemas.lectura import (AlertaSalida, LecturaEntrada, LecturaPlataforma, LecturaSalida,
                                 ResultadoRegistro, ResultadoSincronizacion, SincronizacionLote)
from app.schemas.perfil import (MedicamentoEntrada, MedicamentoSalida, PerfilClinicoEntrada,
                                PerfilClinicoSalida)
from app.schemas.recordatorio import RecordatorioEntrada, RecordatorioProximo, RecordatorioSalida
from app.schemas.usuario import RegistroUsuario, Token, UsuarioSalida

# 6. Asistente con Gemini

La pantalla **Asistente** permite que el paciente haga preguntas sobre la hipertensión y reciba respuestas de **Google Gemini**, limitadas a temas de presión arterial y salud del corazón.

## Paso 1: obtener la llave (API key)

1. Entre a **aistudio.google.com/apikey** con una cuenta de Google.
2. Presione **Create API key** y elija o cree un proyecto.
3. Copie la llave (empieza normalmente por `AIza…`).

## Paso 2: ponerla en el backend

En su computador, en `backend\.env`:

```
GEMINI_API_KEY=AIzaSy...su-llave...
GEMINI_MODELO=gemini-3.5-flash-lite
```

En Render, va en la sección *Environment* del servicio `mi-presion-api` (la guía 8 lo explica).

Reinicie el backend. En la pantalla Asistente desaparecerá el aviso "El asistente aún no está activado".

## ¿Por qué la llave va en el backend y no en la página?

Todo lo que está en el frontend lo puede ver cualquier persona (basta con presionar F12 en el navegador). Si la llave estuviera ahí, alguien podría copiarla y gastar toda su cuota. Por eso:

```
Paciente → frontend → backend (tiene la llave) → Gemini
```

El navegador solo envía la pregunta a `/asistente/preguntar`; el backend agrega la llave y habla con Google.

## ¿Qué modelo usar?

El modelo se cambia con la variable `GEMINI_MODELO`, sin tocar el código.

| Modelo | Ventaja | Plan gratuito (aprox., octubre 2026) |
| --- | --- | --- |
| `gemini-3.5-flash-lite` (predeterminado) | Rápido y con más consultas gratis | Unas 500 consultas al día |
| `gemini-3.8-flash` | Respuestas más elaboradas | Unas 20 consultas al día |

Google cambia sus modelos y límites con frecuencia. Si un modelo deja de existir, consulte la lista actual en ai.google.dev/gemini-api/docs/models y cambie `GEMINI_MODELO`. Los límites exactos de su proyecto aparecen en AI Studio, en la sección de límites de uso. Tenga en cuenta además que, en el plan gratuito, Google puede usar las conversaciones para mejorar sus productos; para un uso real con pacientes conviene activar facturación.

## Cómo se limita a temas de salud

El archivo `backend/app/services/asistente_ia.py` usa cuatro capas de protección:

1. **Instrucciones de sistema**: un texto que Gemini recibe antes de cada pregunta. Le indica que solo hable de hipertensión, alimentación, ejercicio, medicamentos en general y salud cardiovascular. Ante cualquier otro tema debe responder: *"Solo puedo ayudarle con temas de presión arterial y salud del corazón."* También le prohíbe diagnosticar y cambiar dosis de medicamentos.
2. **Detector de emergencias propio**: antes de llamar a Gemini, el backend busca frases como "dolor en el pecho" o "no puedo respirar". Si las encuentra, antepone a la respuesta un aviso para llamar al **123**, sin depender de la IA.
3. **Límite de uso**: cada paciente puede hacer hasta 20 preguntas por hora (variable `ASISTENTE_LIMITE_POR_HORA`). Así se protege la cuota gratuita.
4. **Respuestas personalizadas con permiso**: si el paciente deja marcada la casilla "Usar mis mediciones", el backend agrega un resumen de su última medición y su promedio semanal. Si la desmarca, Gemini no recibe ningún dato suyo.

Para cambiar el comportamiento del asistente, edite el texto `INSTRUCCIONES_SISTEMA` en `asistente_ia.py`.

## Probar sin gastar cuota

Las pruebas automáticas (`backend/tests/test_asistente.py`) reemplazan a Gemini por una función falsa. Así se verifica todo el flujo (permisos, emergencias, límite, errores) sin internet y sin gastar consultas.

## Mensajes de error

| Lo que ve el paciente | Causa | Solución |
| --- | --- | --- |
| "El asistente aún no está activado" | Falta `GEMINI_API_KEY` | Agréguela en `.env` o en Render |
| "La llave de Gemini no es válida" | Llave mal copiada o borrada | Cree una nueva en AI Studio |
| "El asistente recibió muchas preguntas" | Se agotó la cuota gratuita del minuto o del día | Espere, cambie a un modelo *lite* o active facturación |
| "Ha hecho muchas preguntas en la última hora" | El paciente superó el límite por hora | Espere o aumente `ASISTENTE_LIMITE_POR_HORA` |

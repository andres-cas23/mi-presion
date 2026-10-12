# Mi Presión 💙

Aplicación para el monitoreo y control de la hipertensión arterial. Las mediciones llegan solas desde el tensiómetro por Bluetooth, se clasifican según las guías ESC 2024 y generan alertas, promedios semanales e informes para el médico. Además incluye un asistente con inteligencia artificial (Google Gemini) que responde preguntas sobre la enfermedad.

El proyecto está dividido en dos partes independientes:

| Parte | Qué es | Tecnología | Dónde se publica |
| --- | --- | --- | --- |
| `backend/` | El "cerebro": reglas, seguridad y datos | Python + FastAPI | Render (Web Service) |
| `frontend/` | Lo que ve el paciente | HTML + CSS + JavaScript | Render (Static Site) |
| Base de datos | Donde se guardan usuarios y mediciones | PostgreSQL | Supabase |
| Asistente | Responde preguntas sobre hipertensión | Google Gemini | API de Google |

```
Navegador del paciente
        │  (1) abre la página
        ▼
  FRONTEND  ──(2) pide datos──▶  BACKEND  ──(3) guarda/lee──▶  SUPABASE
  (Render)   ◀──(5) responde──   (Render)  ──(4) pregunta───▶  GEMINI
```

## Mapa del repositorio

```
mi-presion/
├── README.md                 ← está aquí
├── render.yaml               ← receta para publicar todo en Render
├── .gitignore                ← archivos que NO se suben a GitHub (p. ej. .env)
├── .github/workflows/        ← GitHub ejecuta las pruebas en cada cambio
├── docs/                     ← guías paso a paso (léalas en orden)
├── backend/                  ← API en Python
│   ├── app/
│   │   ├── main.py           ← punto de entrada
│   │   ├── core/             ← configuración, contraseñas, cifrado, hora
│   │   ├── db/               ← conexión con Supabase
│   │   ├── models/           ← tablas de la base de datos
│   │   ├── schemas/          ← validación de datos que entran y salen
│   │   ├── services/         ← reglas del negocio (clasificar, promediar, Gemini…)
│   │   └── api/rutas/        ← direcciones de la API (/lecturas, /asistente…)
│   ├── tests/                ← pruebas automáticas
│   ├── scripts/              ← simulador de tensiómetro y puente Bluetooth
│   ├── requirements.txt      ← librerías de Python
│   └── .env.example          ← plantilla de configuración secreta
└── frontend/                 ← página web
    ├── index.html            ← única página; las pantallas se dibujan con JS
    ├── css/                  ← estilos (base, estructura, componentes)
    └── js/
        ├── main.js           ← punto de entrada
        ├── config.js         ← dirección del backend
        ├── router.js         ← decide qué pantalla mostrar
        ├── api/              ← comunicación con el backend
        ├── servicios/        ← sesión y Bluetooth
        ├── componentes/      ← piezas reutilizables (gráfico, escala…)
        ├── vistas/           ← una pantalla por archivo
        └── utils/            ← ayudas pequeñas
```

## Guías (léalas en este orden)

1. [Conceptos básicos](docs/01-conceptos-basicos.md): qué es un frontend, un backend, una API y una base de datos, explicado con una analogía.
2. [Estructura del backend](docs/02-estructura-backend.md): cada carpeta, su equivalente en Django y el recorrido de una petición.
3. [Estructura del frontend](docs/03-estructura-frontend.md): cómo se arma la página y cómo agregar una pantalla.
4. [Ejecutar en su computador](docs/04-ejecutar-en-su-computador.md): instalación y puesta en marcha en Windows.
5. [Base de datos en Supabase](docs/05-supabase.md): crear el proyecto y conectarlo.
6. [Asistente con Gemini](docs/06-gemini.md): obtener la llave y cómo se limita a temas de salud.
7. [Subir a GitHub](docs/07-github.md): crear el repositorio y subir el código.
8. [Publicar en Render](docs/08-despliegue-render.md): dejar la aplicación en internet, gratis.

## Arranque rápido (Windows, CMD)

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

En otra ventana de CMD:

```cmd
cd frontend
python -m http.server 5500
```

Abra http://127.0.0.1:5500 en el navegador. Los detalles están en la guía 4.

## Requisitos funcionales cubiertos

| Requisito | Dónde está |
| --- | --- |
| RF-01 Perfil de usuario | `api/rutas/auth.py`, `api/rutas/perfil.py` |
| RF-02 Sincronización automática | `services/ble_parser.py`, `api/rutas/dispositivos.py`, `frontend/js/servicios/bluetooth.js` |
| RF-03 Registro con contexto | `services/contexto.py` |
| RF-04 Tendencias y promedios | `services/hbpm.py` |
| RF-05 Clasificación y alertas | `services/clasificacion.py` |
| RF-06 Recordatorios | `services/recordatorios.py` |
| RF-07 Informes PDF/CSV | `services/reportes.py` |
| RF-08 Módulo educativo | `services/educacion.py` |
| RF-09 Registro manual | `api/rutas/lecturas.py` (`/lecturas/manual`) |
| Asistente de IA | `services/asistente_ia.py`, `frontend/js/vistas/asistente.js` |
| Ley 1581 de 2012 | Consentimiento, cifrado AES-256, `api/rutas/privacidad.py` |

> Esta aplicación es educativa y de apoyo al seguimiento. No reemplaza la valoración médica. Los textos clínicos y las respuestas del asistente deben ser revisados por profesionales de la salud antes de un uso real con pacientes.

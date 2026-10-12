# 2. Estructura del backend

El backend está escrito en **Python** con **FastAPI**. Si conoce Django, la organización le resultará familiar; la tabla de abajo muestra las equivalencias.

## Árbol de carpetas

```
backend/
├── app/
│   ├── main.py                ← enciende la aplicación y junta todo
│   │
│   ├── core/                  ← NÚCLEO: piezas que usa todo el proyecto
│   │   ├── config.py          ← lee las variables de entorno (.env)
│   │   ├── seguridad.py       ← contraseñas (bcrypt) y tokens de sesión (JWT)
│   │   ├── cifrado.py         ← cifra datos clínicos con AES-256
│   │   └── tiempo.py          ← hora local de Colombia
│   │
│   ├── db/                    ← BASE DE DATOS
│   │   ├── base.py            ← clase madre de todas las tablas
│   │   ├── sesion.py          ← conexión con Supabase (o SQLite local)
│   │   └── inicializar.py     ← crea las tablas y activa la seguridad RLS
│   │
│   ├── models/                ← MODELOS: una clase = una tabla
│   │   ├── usuario.py         ← usuarios y perfiles clínicos
│   │   ├── medicamento.py
│   │   ├── dispositivo.py     ← tensiómetros
│   │   ├── lectura.py         ← mediciones y alertas
│   │   ├── recordatorio.py
│   │   └── enums.py           ← listas de valores permitidos
│   │
│   ├── schemas/               ← ESQUEMAS: validan lo que entra y sale
│   │   ├── usuario.py, perfil.py, dispositivo.py, lectura.py,
│   │   └── recordatorio.py, asistente.py
│   │
│   ├── services/              ← SERVICIOS: las reglas del negocio
│   │   ├── clasificacion.py   ← ¿150/95 es hipertensión? (ESC 2024)
│   │   ├── hbpm.py            ← promedio de la semana y tendencias
│   │   ├── contexto.py        ← ¿se midió antes o después del medicamento?
│   │   ├── lecturas.py        ← la ruta única para guardar una medición
│   │   ├── ble_parser.py      ← traduce los bytes del tensiómetro Bluetooth
│   │   ├── recordatorios.py
│   │   ├── reportes.py        ← PDF, CSV y FHIR
│   │   ├── educacion.py       ← textos del módulo "Aprender"
│   │   └── asistente_ia.py    ← conversación con Gemini
│   │
│   └── api/                   ← API: las "puertas" del backend
│       ├── router.py          ← junta todas las rutas
│       ├── dependencias.py    ← "¿quién está conectado?" (protege las rutas)
│       └── rutas/             ← un archivo por tema
│           ├── auth.py        ← /auth/registro, /auth/token
│           ├── perfil.py      ← /perfil, /perfil/medicamentos
│           ├── dispositivos.py← /dispositivos, sincronización Bluetooth
│           ├── lecturas.py    ← /lecturas, /lecturas/manual, /lecturas/hbpm
│           ├── alertas.py, recordatorios.py, reportes.py,
│           ├── educacion.py, privacidad.py
│           └── asistente.py   ← /asistente/preguntar
│
├── tests/                     ← pruebas automáticas (pytest)
├── scripts/                   ← herramientas: simulador y puente Bluetooth
├── requirements.txt           ← lista de librerías
└── .env.example               ← plantilla de configuración
```

## Equivalencias con Django

| En Django | En este proyecto | Para qué sirve |
| --- | --- | --- |
| `settings.py` | `core/config.py` | Configuración general |
| `models.py` | `models/` | Definir las tablas |
| `forms.py` / `serializers.py` | `schemas/` | Validar datos |
| `views.py` | `api/rutas/` | Atender cada petición |
| `urls.py` | `api/router.py` | Conectar direcciones con vistas |
| Lógica dentro de las vistas o en `utils.py` | `services/` | Reglas del negocio, separadas |
| `templates/` | La carpeta `frontend/` completa | Lo que ve el usuario |
| `migrations/` | `db/inicializar.py` | Crear las tablas |
| `manage.py runserver` | `uvicorn app.main:app --reload` | Encender el servidor |

La diferencia principal con Django es que aquí el backend **no genera páginas HTML**: solo responde datos en JSON. Las páginas las arma el frontend por su cuenta.

## Las capas y la regla de oro

Cada capa solo habla con la que tiene al lado:

```
api/rutas  →  schemas  →  services  →  models / db
 (recibe)    (valida)     (piensa)     (guarda)
```

- Las **rutas** no hacen cálculos: reciben el pedido, llaman a un servicio y devuelven el resultado.
- Los **servicios** no saben nada de internet: solo reglas. Por eso se pueden probar fácilmente.
- Los **modelos** no tienen lógica: solo describen las tablas.

## Recorrido de una petición: registrar una medición a mano

Cuando el paciente escribe 150/95 y presiona "Guardar medición":

1. El navegador envía `POST /lecturas/manual` con `{"sistolica": 150, "diastolica": 95}` y su token.
2. `main.py` recibe el pedido y lo pasa a `api/router.py`, que lo dirige a `api/rutas/lecturas.py`, función `registrar_manual`.
3. `api/dependencias.py` lee el token y entrega el usuario. Si el token no es válido, responde "Su sesión terminó" y todo se detiene.
4. `schemas/lectura.py` (clase `LecturaEntrada`) valida que los números estén en rango y que el de arriba sea mayor que el de abajo.
5. La ruta llama a `services/lecturas.py`, función `registrar_lectura`, que:
   - revisa que no sea una medición repetida,
   - usa `services/contexto.py` para deducir si fue antes o después del medicamento,
   - usa `services/clasificacion.py` para obtener la categoría ("hipertensión"),
   - crea un objeto `Lectura` (de `models/lectura.py`) y, si hace falta, una `Alerta`.
6. `db/sesion.py` guarda todo en Supabase.
7. La ruta devuelve la respuesta en JSON y el frontend la muestra.

## Receta: agregar una funcionalidad nueva

Ejemplo: registrar el peso del paciente.

1. **Modelo**: cree `models/peso.py` con la clase `Peso` (columnas `usuario_id`, `kilos`, `medido_en`) e impórtela en `models/__init__.py`.
2. **Esquemas**: cree `schemas/peso.py` con `PesoEntrada` (valida que los kilos estén entre 20 y 300) y `PesoSalida`.
3. **Servicio** (si hay lógica): por ejemplo `services/peso.py` con una función que calcule el índice de masa corporal.
4. **Ruta**: cree `api/rutas/peso.py` con un `router` y las funciones `GET /peso` y `POST /peso`.
5. **Registro**: agregue `peso` a la lista en `api/router.py`.
6. **Prueba**: cree `tests/test_peso.py`.
7. Reinicie el servidor: la tabla se crea sola y la ruta aparece en `/docs`.

## La documentación automática

Con el backend encendido, abra `http://127.0.0.1:8000/docs`. FastAPI genera esa página leyendo el código: muestra todas las rutas, qué datos esperan y permite probarlas. Es la herramienta del desarrollador; el paciente usa el frontend.

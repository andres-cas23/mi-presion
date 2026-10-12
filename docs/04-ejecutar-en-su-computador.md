# 4. Ejecutar en su computador (Windows)

Necesitará **dos ventanas de CMD** abiertas al tiempo: una para el backend y otra para el frontend.

## Requisitos

- **Python 3.11 o superior**. Descárguelo de python.org y, al instalarlo, marque la casilla **"Add Python to PATH"**. Compruebe con `python --version`.
- **Git** (para la guía 7). Descárguelo de git-scm.com.
- Un editor de código. Se recomienda **Visual Studio Code**.

## Paso 1: preparar el backend (solo la primera vez)

Abra CMD en la carpeta del proyecto y ejecute:

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
```

Qué hace cada línea:

- `python -m venv .venv` crea un **entorno virtual**: una caja aislada donde se instalan las librerías de este proyecto sin mezclarse con otros.
- `activate.bat` entra a esa caja. Sabrá que funcionó porque la línea empieza con `(.venv)`.
- `pip install` descarga las librerías listadas en `requirements.txt`.
- `copy` crea su archivo `.env` de configuración a partir de la plantilla.

Si usa **PowerShell** en lugar de CMD, active el entorno con `.venv\Scripts\Activate.ps1`.

## Paso 2: configurar el archivo `.env`

Abra `backend\.env` con su editor. Para practicar, puede dejarlo como viene: sin `DATABASE_URL` se usa una base de datos local (un archivo `mi_presion.db`). Para usar Supabase y Gemini, siga las guías 5 y 6.

## Paso 3: encender el backend

```cmd
uvicorn app.main:app --reload
```

Cuando vea `Application startup complete`, el backend está listo en http://127.0.0.1:8000. Abra http://127.0.0.1:8000/docs para ver todas las rutas.

`--reload` hace que el servidor se reinicie solo cada vez que guarda un cambio en el código. Para apagarlo, presione `Ctrl + C`.

## Paso 4: encender el frontend

Abra **otra** ventana de CMD en la carpeta del proyecto:

```cmd
cd frontend
python -m http.server 5500
```

Abra **http://127.0.0.1:5500** en Chrome o Edge. Verá la pantalla de acceso.

> El frontend debe abrirse por `http://` y no haciendo doble clic en `index.html`. Los navegadores no permiten cargar módulos de JavaScript desde un archivo local.

## Paso 5: cargar datos de demostración (opcional)

En una tercera ventana, con el backend encendido:

```cmd
cd backend
.venv\Scripts\activate.bat
python -m scripts.simulador_tensiometro --crisis
```

Esto crea el usuario `demo@ejemplo.co` (contraseña `Demo12345`) con una semana de mediciones simuladas de tensiómetro Bluetooth, incluida una crisis hipertensiva, y descarga `informe_demo.pdf`.

## Paso 6: ejecutar las pruebas

```cmd
cd backend
.venv\Scripts\activate.bat
python -m pytest -q
```

Debe ver `47 passed`. Ejecútelas cada vez que cambie algo: si alguna falla, el cambio rompió algo.

## Cada vez que vuelva a trabajar

Solo necesita:

```cmd
cd backend
.venv\Scripts\activate.bat
uvicorn app.main:app --reload
```

y en otra ventana:

```cmd
cd frontend
python -m http.server 5500
```

## Problemas comunes

| Mensaje | Causa | Solución |
| --- | --- | --- |
| `'python' no se reconoce` | Python no está en el PATH | Use `py` en lugar de `python`, o reinstale marcando "Add Python to PATH" |
| `'uvicorn' no se reconoce` | El entorno virtual no está activado | Ejecute `.venv\Scripts\activate.bat` (debe ver `(.venv)`) |
| `No module named 'app'` | Está en la carpeta equivocada | Ejecute los comandos desde `backend\` |
| `Could not open requirements file` | Está en la carpeta equivocada | Entre a `backend\` con `cd backend` |
| La página dice "No hay conexión con el servidor" | El backend está apagado | Encienda el backend (paso 3) |
| `address already in use` | Ya hay un servidor en ese puerto | Cierre la otra ventana o use `--port 8001` |

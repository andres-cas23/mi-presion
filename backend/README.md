# Backend de Mi Presión

API en Python (FastAPI). La explicación de cada carpeta está en `docs/02-estructura-backend.md`.

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Pruebas: `python -m pytest -q`
- Datos de demostración: `python -m scripts.simulador_tensiometro --crisis`

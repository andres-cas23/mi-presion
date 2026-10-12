# 5. Base de datos en Supabase

**Supabase** ofrece una base de datos **PostgreSQL** en la nube con un plan gratuito. Ahí quedarán guardados los usuarios que se registren y sus mediciones.

## Cómo la usa este proyecto

El backend se conecta a Supabase como a cualquier base de datos PostgreSQL, usando SQLAlchemy. No hace falta crear tablas a mano: **el backend las crea solo la primera vez que arranca** (`app/db/inicializar.py`).

El inicio de sesión lo maneja nuestro propio backend (contraseñas con bcrypt y tokens JWT), no Supabase Auth. Así toda la lógica queda en un solo lugar y es más fácil de explicar.

## Paso 1: crear la cuenta y el proyecto

1. Entre a **supabase.com** y cree una cuenta (puede usar su cuenta de GitHub).
2. Presione **New project**.
3. Complete:
   - **Name**: `mi-presion`.
   - **Database Password**: invente una contraseña fuerte y **guárdela**, porque la necesitará en el paso 2. Para evitar problemas, use solo letras y números (sin `@`, `#`, `/`, `:` ni `%`), pero bastante larga, por ejemplo de 20 caracteres.
   - **Region**: **East US (North Virginia)**. Es la región más cercana al servidor de Render que usaremos (`virginia`).
4. Presione **Create new project** y espere uno o dos minutos.

## Paso 2: copiar la dirección de conexión

1. En su proyecto, presione el botón **Connect** de la parte superior.
2. Elija la pestaña o el tipo **Session pooler**. Es importante: Render solo puede conectarse por IPv4, y la conexión directa de Supabase usa IPv6. El *Session pooler* sí funciona por IPv4 y es gratis.
3. Copie la **URI**. Se ve así:
   ```
   postgresql://postgres.abcdefghijklmnop:[YOUR-PASSWORD]@aws-1-us-east-1.pooler.supabase.com:5432/postgres
   ```
4. Reemplace `[YOUR-PASSWORD]` (incluidos los corchetes) por la contraseña del paso 1.

Fíjese en dos detalles: el usuario es `postgres.` seguido de un código (no solo `postgres`) y el puerto es `5432`.

## Paso 3: conectar el backend en su computador

1. Abra `backend\.env` y pegue la dirección:
   ```
   DATABASE_URL=postgresql://postgres.abcdefghijklmnop:SuClaveLarga123@aws-1-us-east-1.pooler.supabase.com:5432/postgres
   ```
2. Defina también una `ENCRYPTION_KEY` definitiva. Genérela con:
   ```cmd
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   y pegue el resultado. **No la cambie después**: los datos clínicos guardados con ella no se podrían leer con otra.
3. Encienda el backend (`uvicorn app.main:app --reload`). En la consola verá el mensaje `Tablas listas en PostgreSQL con RLS activado`.

## Paso 4: ver los datos

1. En Supabase, abra **Table Editor** en el menú izquierdo.
2. Verá las tablas `usuarios`, `lecturas`, `alertas`, `medicamentos`, `dispositivos`, `recordatorios` y `perfiles_clinicos`.
3. Cree una cuenta en la aplicación y registre una medición: aparecerá en `lecturas`.

En la tabla `perfiles_clinicos`, columnas como `antecedentes` aparecen como texto ilegible. Es intencional: están **cifradas con AES-256** y solo el backend, que tiene la `ENCRYPTION_KEY`, puede leerlas. La columna `hashed_password` tampoco muestra contraseñas reales.

## ¿Qué es el aviso de "RLS"?

Supabase publica automáticamente una API para cada tabla. Si no se protege, alguien con la llave pública del proyecto podría leer los datos por esa vía. Por eso el backend activa **Row Level Security (RLS)** en todas las tablas al arrancar: esa API pública queda bloqueada, y solo nuestro backend, que se conecta como dueño de las tablas, puede leer y escribir. En el Table Editor verá las tablas marcadas con RLS activado; es lo correcto.

## Tablas que se crean

| Tabla | Qué guarda |
| --- | --- |
| `usuarios` | Correo, nombre, contraseña cifrada y fecha del consentimiento |
| `perfiles_clinicos` | Presión habitual, metas, factores de riesgo (cifrados) |
| `medicamentos` | Nombre y dosis (cifrados), horarios |
| `dispositivos` | Tensiómetros vinculados |
| `lecturas` | Cada medición: valores, fecha, categoría, contexto, origen |
| `alertas` | Avisos de presión muy alta o muy baja |
| `recordatorios` | Medición, medicamento o cita |

## A tener en cuenta en el plan gratuito

- Supabase **pausa los proyectos gratuitos** que pasan una semana sin actividad. Si eso ocurre, entre al panel y presione **Restore project**. Los datos no se pierden.
- El espacio gratuito alcanza de sobra para un piloto con cientos de pacientes.

## Problemas comunes

| Mensaje | Causa | Solución |
| --- | --- | --- |
| `password authentication failed` | Contraseña equivocada en la URL | Revise que reemplazó `[YOUR-PASSWORD]` sin dejar los corchetes |
| `no tenant identifier provided` | Usuario sin el código del proyecto | El usuario debe ser `postgres.SU_CODIGO`, no `postgres` |
| `could not translate host name` o tiempo de espera agotado | Usó la conexión directa (IPv6) | Use la URI del **Session pooler** |
| Error con caracteres raros en la contraseña | La contraseña tiene `@`, `#`, `/`… | Cambie la contraseña en *Project Settings → Database* por una solo con letras y números |

# 8. Publicar en Render (gratis)

Al terminar esta guía, la aplicación tendrá una dirección pública como `https://mi-presion-web.onrender.com`, donde cualquier persona podrá registrarse e ingresar.

## ¿Por qué Render y no Railway?

| | Render | Railway |
| --- | --- | --- |
| Plan gratuito permanente | Sí: un servicio web y sitios estáticos | No: solo créditos de prueba |
| Página estática (frontend) | Gratis, sin límite de tiempo | Consume créditos |
| Limitación | El backend "se duerme" tras 15 minutos sin uso | Se acaba el crédito |

**Sobre el "sueño" del backend gratuito**: si nadie usa la aplicación durante 15 minutos, Render apaga el backend. La siguiente persona que entre esperará entre 30 y 60 segundos mientras despierta. El frontend ya lo tiene en cuenta: muestra el aviso *"El servidor gratuito se está despertando…"*. Para una demostración, abra la página un minuto antes.

## Antes de empezar

Debe tener:

- [ ] El código en GitHub (guía 7).
- [ ] La dirección del *Session pooler* de Supabase con su contraseña (guía 5).
- [ ] Su llave de Gemini (guía 6).

## Paso 1 (recomendado): nombres únicos

Las direcciones de Render dependen del nombre del servicio. Si otra persona ya usa `mi-presion-api`, Render le agregará letras al azar. Para evitar confusiones, abra `render.yaml` y agregue su nombre o un número a los dos servicios:

```yaml
    name: mi-presion-api-andres
...
    name: mi-presion-web-andres
```

Guarde y suba el cambio:

```cmd
git add .
git commit -m "Nombres de servicios en Render"
git push
```

## Paso 2: crear la cuenta en Render

1. Entre a **render.com** y presione **Get Started**.
2. Regístrese **con GitHub**. Así Render podrá ver sus repositorios.

## Paso 3: crear los servicios con el Blueprint

1. En el panel de Render presione **New +** → **Blueprint**.
2. Elija el repositorio `mi-presion`. Si no aparece, presione *Configure account* y dele acceso a Render.
3. Render lee `render.yaml` y muestra los dos servicios. Le pedirá los valores marcados como secretos:

| Variable | Qué poner |
| --- | --- |
| `DATABASE_URL` | La URI del *Session pooler* de Supabase, con su contraseña |
| `GEMINI_API_KEY` | Su llave de Gemini |
| `API_URL` | `https://` + el nombre de su backend + `.onrender.com`, por ejemplo `https://mi-presion-api-andres.onrender.com` (sin `/` al final) |

4. Presione **Apply** (o *Deploy Blueprint*).

Render instalará todo. El backend tarda entre 3 y 5 minutos la primera vez; el frontend, menos de uno. Puede ver el avance en la pestaña **Logs** de cada servicio.

`SECRET_KEY` y `ENCRYPTION_KEY` las genera Render automáticamente. No modifique `ENCRYPTION_KEY` después: perdería el acceso a los datos cifrados.

## Paso 4: comprobar el backend

1. Abra el servicio **mi-presion-api** en Render. Arriba verá su dirección real.
2. Ábrala en el navegador. Debe ver:
   ```json
   {"servicio":"Mi Presión API","estado":"ok","documentacion":"/docs"}
   ```
3. **Compare** esa dirección con la que escribió en `API_URL`. Si es distinta (por ejemplo, Render agregó letras), vaya al servicio **mi-presion-web** → **Environment**, corrija `API_URL`, guarde y luego presione **Manual Deploy** → **Deploy latest commit**.

## Paso 5: probar la aplicación

1. Abra el servicio **mi-presion-web** y entre a su dirección.
2. Cree una cuenta, agregue un tensiómetro y presione **Simular medición**.
3. Revise en Supabase (**Table Editor** → `lecturas`) que la medición quedó guardada.
4. Haga una pregunta en **Asistente**.

¡Listo! Comparta la dirección del frontend con quien quiera probar la aplicación.

## Paso 6 (recomendado): restringir quién usa la API

Por ahora `CORS_ORIGINS` vale `*`, es decir, cualquier página puede llamar a su backend. Para que solo lo use su frontend:

1. Copie la dirección de **mi-presion-web** (por ejemplo `https://mi-presion-web-andres.onrender.com`).
2. En **mi-presion-api** → **Environment**, cambie `CORS_ORIGINS` por esa dirección, sin `/` al final.
3. Guarde. Render reinicia el backend solo.

## Cargar datos de demostración en la versión publicada

Desde su computador, con el entorno virtual activado:

```cmd
cd backend
python -m scripts.simulador_tensiometro --api https://mi-presion-api-andres.onrender.com --crisis
```

## Publicar cambios

Cada `git push` a la rama `main` hace que Render vuelva a publicar automáticamente los servicios.

## Problemas comunes

| Síntoma | Causa | Solución |
| --- | --- | --- |
| La página dice "No hay conexión con el servidor" | `API_URL` mal escrita o el backend falló | Revise el paso 4 y los *Logs* del backend |
| En los logs: `password authentication failed` | Contraseña de Supabase mal puesta | Corrija `DATABASE_URL` en *Environment* |
| En los logs: `Network is unreachable` o tiempo agotado hacia Supabase | Usó la conexión directa (IPv6) | Use la URI del **Session pooler** |
| Error de CORS en la consola del navegador (F12) | `CORS_ORIGINS` no coincide con la dirección del frontend | Póngala exactamente igual, sin `/` final, o vuelva a `*` |
| La primera carga tarda casi un minuto | El backend gratuito estaba dormido | Es normal en el plan gratuito |
| El asistente dice que no está activado | Falta `GEMINI_API_KEY` | Agréguela en *Environment* de **mi-presion-api** |
| Cambié `API_URL` pero no se refleja | El frontend no se reconstruyó | *Manual Deploy* → *Deploy latest commit* en **mi-presion-web** |

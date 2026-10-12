# 7. Subir el proyecto a GitHub

**GitHub** guarda el código en internet con todo su historial de cambios. Render lo necesita: cada vez que usted sube un cambio a GitHub, Render publica la nueva versión automáticamente.

## Antes de empezar: proteja sus secretos

El archivo `backend\.env` contiene la contraseña de Supabase y la llave de Gemini. **Nunca debe subirse.** El archivo `.gitignore` ya lo excluye, pero en el paso 4 lo verificaremos.

## Paso 1: instalar Git y crear la cuenta

1. Descargue Git de **git-scm.com** e instálelo con las opciones predeterminadas.
2. Cree una cuenta en **github.com**.
3. Abra una ventana nueva de CMD y configure su nombre y correo (solo una vez):
   ```cmd
   git config --global user.name "Su Nombre"
   git config --global user.email "su-correo@ejemplo.com"
   ```

## Paso 2: crear el repositorio vacío en GitHub

1. En GitHub, presione **New** (o el botón **+** arriba a la derecha → *New repository*).
2. **Repository name**: `mi-presion`.
3. Puede dejarlo **Public** o **Private**; Render funciona con ambos.
4. **No** marque "Add a README", ".gitignore" ni "license": el proyecto ya los tiene.
5. Presione **Create repository**. Deje abierta esa página: muestra la dirección del repositorio, algo como `https://github.com/SU-USUARIO/mi-presion.git`.

## Paso 3: subir el código

En CMD, entre a la carpeta raíz del proyecto, la que contiene `backend`, `frontend` y `README.md`:

```cmd
cd ruta\a\mi-presion
git init
git add .
git status
```

## Paso 4: verificar que `.env` NO aparezca

En el resultado de `git status`, revise la lista de archivos en verde. **No debe aparecer** `backend/.env`, ni `.venv`, ni archivos `.db`. Si aparece `.env`, deténgase y revise que el archivo `.gitignore` esté en la carpeta raíz.

## Paso 5: guardar y enviar

```cmd
git commit -m "Primera versión de Mi Presión"
git branch -M main
git remote add origin https://github.com/SU-USUARIO/mi-presion.git
git push -u origin main
```

La primera vez, Windows abrirá una ventana para iniciar sesión en GitHub. Hágalo desde el navegador y autorice.

Recargue la página del repositorio en GitHub: verá todas las carpetas.

## Qué significa cada comando

| Comando | Qué hace |
| --- | --- |
| `git init` | Convierte la carpeta en un repositorio (empieza a llevar historial) |
| `git add .` | Marca todos los archivos para el próximo guardado |
| `git status` | Muestra qué cambió y qué está marcado |
| `git commit -m "mensaje"` | Guarda una "foto" del proyecto con una descripción |
| `git branch -M main` | Llama `main` a la rama principal |
| `git remote add origin URL` | Conecta su carpeta con el repositorio de GitHub |
| `git push` | Sube los cambios a GitHub |

## Cada vez que haga cambios

```cmd
git add .
git commit -m "Describa el cambio, ej.: agrega pantalla de peso"
git push
```

Render detecta el `push` y publica la nueva versión en pocos minutos.

## Pruebas automáticas en GitHub

El archivo `.github/workflows/pruebas.yml` hace que GitHub ejecute las 47 pruebas cada vez que sube cambios. El resultado aparece en la pestaña **Actions** del repositorio: una marca verde significa que todo está bien y una X roja, que algo se rompió.

## Si subió `.env` por error

1. Bórrelo del repositorio (sin borrarlo de su computador):
   ```cmd
   git rm --cached backend/.env
   git commit -m "Quita .env"
   git push
   ```
2. **Cambie de inmediato** la contraseña de Supabase y cree una llave nueva de Gemini: aunque borre el archivo, queda en el historial y alguien pudo verlo.

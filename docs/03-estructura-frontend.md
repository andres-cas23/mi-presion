# 3. Estructura del frontend

El frontend está hecho con **HTML, CSS y JavaScript**, sin herramientas que haya que compilar. Eso lo hace fácil de entender y de publicar: los archivos se suben tal cual.

- **HTML** define *qué hay* en la página (títulos, botones, cajas).
- **CSS** define *cómo se ve* (colores, tamaños, posiciones).
- **JavaScript** define *qué hace* (responder a clics, pedir datos al backend, dibujar pantallas).

## Árbol de carpetas

```
frontend/
├── index.html                 ← la única página: contiene el menú y un espacio vacío
│                                (<main id="contenido">) donde se dibuja cada pantalla
├── css/
│   ├── base.css               ← colores, letra, botones y formularios
│   ├── estructura.css         ← menú lateral / barra inferior y pantalla de acceso
│   └── componentes.css        ← piezas: avisos, gráfico, escala, chat…
└── js/
    ├── main.js                ← PUNTO DE ENTRADA: decide si mostrar acceso o la app
    ├── config.js              ← dirección del backend (API_URL)
    ├── router.js              ← según la dirección (#/inicio, #/perfil…) elige la pantalla
    │
    ├── api/
    │   └── cliente.js         ← ÚNICA puerta para hablar con el backend
    │
    ├── servicios/
    │   ├── sesion.js          ← iniciar sesión, crear cuenta, cerrar sesión
    │   └── bluetooth.js       ← conectar con el tensiómetro real o simularlo
    │
    ├── componentes/           ← piezas visuales que se usan en varias pantallas
    │   ├── escala.js          ← barra de colores verde → rojo
    │   ├── grafico.js         ← gráfico de líneas de 30 días
    │   └── texto_enriquecido.js ← da formato a las respuestas del asistente
    │
    ├── vistas/                ← UNA PANTALLA POR ARCHIVO
    │   ├── acceso.js          ← entrar / crear cuenta
    │   ├── inicio.js          ← última medición, semana, gráfico, recordatorios
    │   ├── mediciones.js      ← tensiómetros, historial, registro manual
    │   ├── asistente.js       ← chat con Gemini
    │   ├── informes.js        ← descargar PDF y CSV
    │   ├── aprender.js        ← temas educativos
    │   └── perfil.js          ← medicamentos, citas, datos, privacidad
    │
    └── utils/                 ← ayudas pequeñas
        ├── dom.js             ← buscar elementos, mensajes emergentes, descargas
        ├── formato.js         ← fechas y textos ("Hoy a las 7:10 a. m.")
        ├── navegar.js         ← cambiar de pantalla
        └── tam_texto.js       ← tamaño de la letra
```

## Equivalencias con Django

| En Django | En este frontend |
| --- | --- |
| `templates/base.html` | `index.html` (menú y estructura común) |
| Una plantilla por página (`inicio.html`) | Un archivo por pantalla en `js/vistas/` |
| `{% include "grafico.html" %}` | Funciones en `js/componentes/` (por ejemplo `grafico(lecturas)`) |
| `urls.py` | `js/router.js` |
| `static/css/` | `css/` |

## Cómo se conecta todo

```
index.html
   └── carga js/main.js
          ├── ¿hay sesión? NO → vistas/acceso.js dibuja el formulario de entrada
          └── ¿hay sesión? SÍ → router.js
                                   └── lee la dirección (#/inicio)
                                         └── vistas/inicio.js
                                               ├── pide datos con api/cliente.js → BACKEND
                                               └── dibuja usando componentes/grafico.js, escala.js…
```

Cada vista exporta una función `mostrar(contenedor)`. El router la llama, la vista pide los datos que necesita y escribe su HTML dentro del contenedor.

## ¿Por qué `#/inicio` en la dirección?

La parte después de `#` le dice al router qué pantalla mostrar, sin recargar la página. Así funcionan los botones de atrás y adelante del navegador, y se puede compartir un enlace directo, por ejemplo `.../#/aprender/dieta-dash-colombiana`.

## Dónde vive la dirección del backend

En `js/config.js`:

```js
export const API_URL = "http://127.0.0.1:8000";
```

En su computador apunta al backend local. Al publicar en Render, el archivo se reescribe automáticamente con la dirección real (vea `render.yaml`).

## Receta: agregar una pantalla nueva

Ejemplo: una pantalla "Mi peso".

1. Cree `js/vistas/peso.js`:
   ```js
   import { api } from "../api/cliente.js";
   import { esc } from "../utils/dom.js";

   export async function mostrar(c) {
     const pesos = await api("/peso");
     c.innerHTML = `<div class="encabezado"><h1>Mi peso</h1></div>
       <section class="bloque">${pesos.map((p) => `<p>${esc(p.kilos)} kg</p>`).join("")}</section>`;
   }
   ```
2. En `js/router.js`, importe la vista y agréguela a `RUTAS`:
   ```js
   import * as peso from "./vistas/peso.js";
   const RUTAS = { inicio, mediciones, asistente, informes, aprender, perfil, peso };
   ```
3. En `index.html`, agregue un enlace al menú: `<a href="#/peso" data-ruta="peso">Mi peso</a>`.

## Accesibilidad (pensada para adultos mayores)

- Letra **Atkinson Hyperlegible**, diseñada para personas con baja visión, a 19 px y con tres tamaños.
- Botones de al menos 52 px de alto.
- Colores azules y verdes con buen contraste; el rojo se reserva para alertas.
- Menú siempre visible: a la izquierda en computador y abajo en celular.
- Frases sencillas: "número de arriba" además de "sistólica".

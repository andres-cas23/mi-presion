// =========================================================
// ENRUTADOR: decide qué pantalla mostrar según la dirección.
//   #/inicio            -> vistas/inicio.js
//   #/aprender/dieta... -> vistas/aprender.js con el tema "dieta..."
// Equivale a urls.py de Django, pero en el navegador.
// =========================================================
import * as aprender from "./vistas/aprender.js";
import * as asistente from "./vistas/asistente.js";
import * as informes from "./vistas/informes.js";
import * as inicio from "./vistas/inicio.js";
import * as mediciones from "./vistas/mediciones.js";
import * as perfil from "./vistas/perfil.js";
import { $, $$, esc } from "./utils/dom.js";

const RUTAS = { inicio, mediciones, asistente, informes, aprender, perfil };


export async function mostrarRutaActual() {
  const [nombre = "inicio", ...parametros] = location.hash.replace(/^#\/?/, "").split("/");
  const vista = RUTAS[nombre] || inicio;

  $$(".menu [data-ruta]").forEach((a) =>
    a.dataset.ruta === nombre ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));

  const contenedor = $("#contenido");
  contenedor.innerHTML = `<p class="vacio">Cargando…</p>`;
  try {
    await vista.mostrar(contenedor, ...parametros.map(decodeURIComponent));
  } catch (err) {
    contenedor.innerHTML = `<div class="aviso urgente"><strong>No se pudo cargar esta sección</strong>${esc(err.message)}</div>`;
  }
  contenedor.focus({ preventScroll: true });
  window.scrollTo(0, 0);
}

export function iniciarRouter() {
  window.addEventListener("hashchange", mostrarRutaActual);
  mostrarRutaActual();
}

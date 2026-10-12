// =========================================================
// PUNTO DE ENTRADA DEL FRONTEND
// 1. Aplica el tamaño de letra guardado.
// 2. Si hay sesión, muestra la aplicación; si no, la pantalla de acceso.
// =========================================================
import { mostrarRutaActual, iniciarRouter } from "./router.js";
import { api } from "./api/cliente.js";
import { cargarUsuario, haySesion } from "./servicios/sesion.js";
import { $, $$ } from "./utils/dom.js";
import { aplicarTamGuardado, cambiarTamTexto } from "./utils/tam_texto.js";
import * as acceso from "./vistas/acceso.js";

let routerIniciado = false;

function mostrarAcceso() {
  $("#pantalla-app").hidden = true;
  $("#pantalla-acceso").hidden = false;
  acceso.mostrar($("#pantalla-acceso"), mostrarApp);
}

async function mostrarApp() {
  $("#pantalla-acceso").hidden = true;
  $("#pantalla-app").hidden = false;
  if (!location.hash) location.hash = "#/inicio";
  if (routerIniciado) mostrarRutaActual();
  else { iniciarRouter(); routerIniciado = true; }
}

// Botones de tamaño de letra del menú lateral
$$(".texto-tam button").forEach((b) => (b.onclick = () => cambiarTamTexto(b.dataset.tam)));
aplicarTamGuardado();

// Si el token vence o la persona cierra sesión, volvemos a la pantalla de acceso
window.addEventListener("sesion-expirada", mostrarAcceso);

// Despierta el servidor gratuito de Render apenas se abre la página
api("/").catch(() => {});

(async () => {
  if (!haySesion()) return mostrarAcceso();
  try {
    await cargarUsuario();
    mostrarApp();
  } catch {
    mostrarAcceso();
  }
})();

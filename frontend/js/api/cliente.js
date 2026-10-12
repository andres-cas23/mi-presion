// =========================================================
// CLIENTE DE LA API: la única puerta para hablar con el backend.
// Todas las pantallas usan api("/ruta") en vez de fetch directo.
// =========================================================
import { API_URL } from "../config.js";
import { $ } from "../utils/dom.js";

const BASE = API_URL.replace(/\/+$/, ""); // quita la "/" final si la tiene
const CLAVE_TOKEN = "mi-presion-token";

export const obtenerToken = () => localStorage.getItem(CLAVE_TOKEN);
export const guardarToken = (t) => (t ? localStorage.setItem(CLAVE_TOKEN, t) : localStorage.removeItem(CLAVE_TOKEN));

/** Convierte los errores del backend en frases entendibles. */
function traducirError(detalle) {
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle) && detalle.length) {
    const m = detalle[0].msg || "";
    if (m.startsWith("Value error, ")) return m.slice(13);
    return "Revise los datos: hay un valor fuera de rango o incompleto.";
  }
  return "No se pudo completar la acción. Intente de nuevo.";
}

/**
 * Llama al backend.
 *   api("/lecturas")                                  -> GET
 *   api("/lecturas/manual", { metodo: "POST", json }) -> POST con JSON
 *   api("/auth/token", { metodo: "POST", form })      -> POST de formulario
 *   api("/reportes/pdf", { crudo: true })             -> devuelve la respuesta sin procesar
 */
export async function api(ruta, { metodo = "GET", json, form, crudo = false } = {}) {
  const opciones = { method: metodo, headers: {} };
  const token = obtenerToken();
  if (token) opciones.headers.Authorization = `Bearer ${token}`;
  if (json !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(json);
  }
  if (form) opciones.body = new URLSearchParams(form);

  // Render gratuito "duerme" el servidor: si tarda, avisamos al usuario.
  const aviso = setTimeout(() => ($("#despertando").hidden = false), 4000);
  let respuesta;
  try {
    respuesta = await fetch(BASE + ruta, opciones);
  } catch {
    throw new Error("No hay conexión con el servidor. Revise su internet o intente en un momento.");
  } finally {
    clearTimeout(aviso);
    $("#despertando").hidden = true;
  }

  if (respuesta.status === 401 && token) {
    guardarToken(null);
    window.dispatchEvent(new Event("sesion-expirada"));
    throw new Error("Su sesión terminó. Ingrese de nuevo.");
  }
  if (!respuesta.ok) {
    let detalle;
    try { detalle = (await respuesta.json()).detail; } catch { /* sin cuerpo */ }
    throw new Error(traducirError(detalle));
  }
  if (crudo) return respuesta;
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

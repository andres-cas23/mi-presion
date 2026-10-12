// Iniciar sesión, crear cuenta, cerrar sesión y recordar quién está conectado.
import { api, guardarToken, obtenerToken } from "../api/cliente.js";

let usuarioActual = null;

export const usuario = () => usuarioActual;
export const haySesion = () => Boolean(obtenerToken());

export async function iniciarSesion(email, password) {
  const r = await api("/auth/token", { metodo: "POST", form: { username: email, password } });
  guardarToken(r.access_token);
  await cargarUsuario();
}

export async function crearCuenta(datos) {
  await api("/auth/registro", { metodo: "POST", json: datos });
  await iniciarSesion(datos.email, datos.password);
}

export async function cargarUsuario() {
  const perfil = await api("/perfil");
  usuarioActual = perfil.usuario;
  return usuarioActual;
}

export function cerrarSesion() {
  guardarToken(null);
  usuarioActual = null;
  window.dispatchEvent(new Event("sesion-expirada"));
}

// Cambia de pantalla. Si ya está en esa pantalla, la recarga.
export function irA(ruta) {
  if (location.hash === `#/${ruta}`) window.dispatchEvent(new HashChangeEvent("hashchange"));
  else location.hash = `#/${ruta}`;
}

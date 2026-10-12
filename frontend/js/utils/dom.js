// Pequeñas ayudas para trabajar con la página.

/** Busca un elemento: $("#id") */
export const $ = (selector, raiz = document) => raiz.querySelector(selector);
export const $$ = (selector, raiz = document) => [...raiz.querySelectorAll(selector)];

/** Escapa texto antes de ponerlo en HTML (evita que un texto malicioso se ejecute). */
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/** Mensaje corto que aparece abajo y desaparece solo. */
export function toast(mensaje) {
  const t = $("#toast");
  t.textContent = mensaje;
  t.hidden = false;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => (t.hidden = true), 4500);
}

/** Descarga un archivo (Blob) con el nombre indicado. */
export function descargar(blob, nombre) {
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement("a"), { href: url, download: nombre });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
}

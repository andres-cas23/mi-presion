// Tamaño de la letra (normal, grande, muy grande). Se recuerda en este navegador.
const CLAVE = "mi-presion-texto";

export function cambiarTamTexto(tam) {
  document.documentElement.dataset.texto = tam;
  try { localStorage.setItem(CLAVE, tam); } catch { /* navegación privada */ }
  document.querySelectorAll("button[data-tam]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.tam === tam));
}

export function aplicarTamGuardado() {
  let tam = "normal";
  try { tam = localStorage.getItem(CLAVE) || "normal"; } catch { /* sin acceso */ }
  cambiarTamTexto(tam);
}

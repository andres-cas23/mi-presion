// Convierte el texto del asistente (con **negritas** y listas) en HTML seguro.
import { esc } from "../utils/dom.js";

export function textoEnriquecido(texto) {
  const lineas = esc(texto).split("\n");
  let html = "", lista = null;
  const cerrarLista = () => { if (lista) { html += `</${lista}>`; lista = null; } };
  for (const cruda of lineas) {
    const linea = cruda.trim().replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
    const viñeta = linea.match(/^[-*•]\s+(.*)/);
    const numero = linea.match(/^\d+[.)]\s+(.*)/);
    if (viñeta || numero) {
      const tipo = viñeta ? "ul" : "ol";
      if (lista !== tipo) { cerrarLista(); html += `<${tipo}>`; lista = tipo; }
      html += `<li>${(viñeta || numero)[1]}</li>`;
    } else {
      cerrarLista();
      if (linea) html += `<p>${linea.replace(/^#+\s*/, "")}</p>`;
    }
  }
  cerrarLista();
  return html;
}

// =========================================================
// VISTA: APRENDER (lista de temas y artículo)
//   #/aprender            -> lista
//   #/aprender/<tema>     -> artículo
// =========================================================
import { api } from "../api/cliente.js";
import { esc } from "../utils/dom.js";

export async function mostrar(c, tema) {
  if (tema) {
    const a = await api(`/educacion/${encodeURIComponent(tema)}`);
    c.innerHTML = `<div class="fila-botones" style="margin:0 0 1rem"><a class="btn secundario" href="#/aprender">‹ Volver a los temas</a></div>
      <article class="bloque articulo"><h1>${esc(a.titulo)}</h1><p><b>${esc(a.resumen)}</b></p>
      <ul>${a.secciones.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
      <p class="nota">Esta información es orientativa y no reemplaza las indicaciones de su médico.
        ¿Tiene dudas? <a href="#/asistente">Pregúntele al asistente</a>.</p></article>`;
    return;
  }
  const temas = await api("/educacion");
  c.innerHTML = `<div class="encabezado"><h1>Aprender</h1><p>Consejos cortos para cuidar su presión</p></div>
    <div class="temas">${temas.map((t) => `<a class="tema" href="#/aprender/${esc(t.slug)}"><b>${esc(t.titulo)}</b><span>${esc(t.resumen)}</span></a>`).join("")}</div>`;
}

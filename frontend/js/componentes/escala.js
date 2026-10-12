// Barra de colores que muestra dónde cae un valor (verde -> rojo).

/**
 * @param valor  número a marcar (ej. 142)
 * @param min,max  extremos de la barra
 * @param cortes  límites entre colores (ej. [120, 140, 180])
 */
export function escala(valor, min, max, cortes, nombre, nombreTecnico) {
  const pct = (v) => ((Math.min(Math.max(v, min), max) - min) / (max - min)) * 100;
  const tramos = [min, ...cortes, max];
  let segmentos = "";
  for (let i = 0; i < tramos.length - 1; i++) {
    segmentos += `<span class="s${i + 1}" style="width:${pct(tramos[i + 1]) - pct(tramos[i])}%"></span>`;
  }
  return `<div>
    <div class="escala-nombre"><span>${nombre} <span class="nota">(${nombreTecnico})</span></span><b>${valor}</b></div>
    <div class="escala" role="img" aria-label="${nombre}: ${valor} milímetros de mercurio">
      ${segmentos}<div class="marcador" style="left:0%" data-pos="${pct(valor)}"></div>
    </div>
  </div>`;
}

export const leyendaEscala = `<div class="escala-leyenda">
  <span><i style="background:#9FD3B8"></i>No elevada</span><span><i style="background:#F2D38A"></i>Elevada</span>
  <span><i style="background:#F0A988"></i>Hipertensión</span><span><i style="background:#E58A8C"></i>Crisis</span>
</div>`;

/** Mueve los marcadores a su posición con una pequeña animación. */
export function animarEscalas(contenedor) {
  requestAnimationFrame(() => requestAnimationFrame(() =>
    contenedor.querySelectorAll(".marcador").forEach((m) => (m.style.left = m.dataset.pos + "%"))));
}

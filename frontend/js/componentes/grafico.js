// Gráfico de líneas (SVG) con la presión en el tiempo. No usa librerías externas.

export function grafico(lecturas) {
  if (lecturas.length < 2) {
    return `<p class="vacio">Cuando tenga al menos dos mediciones, aquí verá cómo va su presión.</p>`;
  }
  const W = 760, H = 280, iz = 44, de = 34, ar = 14, ab = 36;
  const tiempo = (l) => new Date(l.medido_en).getTime();
  const t0 = tiempo(lecturas[0]), t1 = tiempo(lecturas.at(-1));
  const yMin = 50, yMax = Math.max(190, ...lecturas.map((l) => l.sistolica + 10));
  const X = (t) => iz + ((t - t0) / Math.max(t1 - t0, 1)) * (W - iz - de);
  const Y = (v) => ar + (1 - (v - yMin) / (yMax - yMin)) * (H - ar - ab);
  const linea = (campo) => lecturas.map((l, i) => `${i ? "L" : "M"}${X(tiempo(l)).toFixed(1)},${Y(l[campo]).toFixed(1)}`).join("");

  let guias = "";
  for (let v = 60; v <= yMax; v += 20) {
    guias += `<line x1="${iz}" x2="${W - de}" y1="${Y(v)}" y2="${Y(v)}" stroke="#E3EAE9"/>
      <text x="${iz - 8}" y="${Y(v) + 4}" text-anchor="end" font-size="12" fill="#4A5F73">${v}</text>`;
  }
  const pasos = Math.min(Math.max(1, Math.round((t1 - t0) / 864e5)), 6);
  for (let i = 0; i <= pasos; i++) {
    const t = t0 + ((t1 - t0) * i) / pasos;
    guias += `<text x="${X(t)}" y="${H - 12}" text-anchor="middle" font-size="12" fill="#4A5F73">${new Date(t).toLocaleDateString("es-CO", { day: "numeric", month: "short" })}</text>`;
  }
  const umbral = (v, color) => `<line x1="${iz}" x2="${W - de}" y1="${Y(v)}" y2="${Y(v)}" stroke="${color}" stroke-width="1.5" stroke-dasharray="6 5"/>`;
  const puntos = (campo, color) => lecturas.map((l) => {
    const crisis = l.categoria === "crisis_hipertensiva" && campo === "sistolica";
    return `<circle cx="${X(tiempo(l))}" cy="${Y(l[campo])}" r="${crisis ? 6 : 3.5}" fill="${crisis ? "#A3161A" : color}"/>`;
  }).join("");

  return `<div class="grafico"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Gráfico de su presión en el tiempo">
      ${guias}${umbral(135, "#B0441C")}${umbral(85, "#8A5A00")}
      <path d="${linea("sistolica")}" fill="none" stroke="#1D5C96" stroke-width="2.5" stroke-linejoin="round"/>
      <path d="${linea("diastolica")}" fill="none" stroke="#2A7A57" stroke-width="2.5" stroke-linejoin="round"/>
      ${puntos("sistolica", "#1D5C96")}${puntos("diastolica", "#2A7A57")}
    </svg></div>
    <div class="leyenda-graf">
      <span><i style="background:#1D5C96"></i>Número de arriba (sistólica)</span>
      <span><i style="background:#2A7A57"></i>Número de abajo (diastólica)</span>
      <span><i style="background:repeating-linear-gradient(90deg,#B0441C 0 6px,transparent 6px 10px)"></i>Límite en casa: 135/85</span>
    </div>`;
}

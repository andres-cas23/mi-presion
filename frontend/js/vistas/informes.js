// =========================================================
// VISTA: INFORMES (PDF y CSV para el médico)
// =========================================================
import { api } from "../api/cliente.js";
import { $, descargar, toast } from "../utils/dom.js";
import { fechaLocalISO } from "../utils/formato.js";

export async function mostrar(c) {
  c.innerHTML = `<div class="encabezado"><h1>Informes para su médico</h1></div>
  <section class="bloque">
    <p>Descargue un informe con su promedio en casa, un gráfico y todas sus mediciones. Puede imprimirlo o enviarlo a su médico.</p>
    <label for="r-periodo">Periodo</label>
    <select id="r-periodo">
      <option value="7">Últimos 7 días</option><option value="30" selected>Últimos 30 días</option>
      <option value="90">Últimos 3 meses</option><option value="">Todo el historial</option>
    </select>
    <div class="fila-botones">
      <button class="btn" data-formato="pdf">Descargar informe (PDF)</button>
      <button class="btn secundario" data-formato="csv">Descargar tabla (Excel/CSV)</button>
    </div>
    <details><summary>Para clínicas e instituciones de salud</summary>
      <p class="nota">Formato estándar HL7 FHIR, para integrar los datos con la historia clínica electrónica.</p>
      <button class="btn secundario" data-formato="fhir">Descargar en formato FHIR (JSON)</button>
    </details>
  </section>`;

  c.querySelectorAll("[data-formato]").forEach((b) => (b.onclick = async () => {
    const dias = $("#r-periodo").value, formato = b.dataset.formato;
    const filtro = dias ? `?desde=${fechaLocalISO(Date.now() - dias * 864e5)}` : "";
    b.disabled = true;
    try {
      const r = await api(`/reportes/${formato}${filtro}`, { crudo: true });
      descargar(await r.blob(), `presion_arterial.${formato === "fhir" ? "json" : formato}`);
      toast("Informe descargado.");
    } catch (err) { toast(err.message); }
    b.disabled = false;
  }));
}

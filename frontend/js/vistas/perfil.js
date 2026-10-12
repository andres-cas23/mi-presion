// =========================================================
// VISTA: MI PERFIL (medicamentos, recordatorios, datos de
// salud, tamaño del texto y privacidad)
// =========================================================
import { api } from "../api/cliente.js";
import { cerrarSesion } from "../servicios/sesion.js";
import { $, descargar, esc, toast } from "../utils/dom.js";
import { fechaLarga, TIPOS_RECORDATORIO } from "../utils/formato.js";
import { irA } from "../utils/navegar.js";
import { cambiarTamTexto } from "../utils/tam_texto.js";

export async function mostrar(c) {
  const [p, meds, recs] = await Promise.all([api("/perfil"), api("/perfil/medicamentos"), api("/recordatorios")]);
  const v = (x) => x ?? "";

  c.innerHTML = `<div class="encabezado"><h1>Mi perfil</h1><p>${esc(p.usuario.email)}</p></div>

  <section class="bloque"><h2>Mis medicamentos</h2>
    ${meds.length ? `<ul class="lista">${meds.map((m) => `<li>
        <span><span class="principal">${esc(m.nombre)}</span> <span class="sec">${esc(m.dosis || "")}</span><br>
        <span class="sec">${m.horarios.length ? "A las " + m.horarios.join(" y ") : "Sin horario"}</span></span>
        <button class="boton-texto rojo" data-med="${m.id}">Ya no lo tomo</button></li>`).join("")}</ul>`
      : `<p class="vacio">No ha registrado medicamentos.</p>`}
    <details><summary>Agregar un medicamento</summary>
      <form id="form-med">
        <div class="dos-col">
          <div><label for="md-nom">Nombre</label><input id="md-nom" required placeholder="Ej.: Losartán"></div>
          <div><label for="md-dosis">Dosis</label><input id="md-dosis" placeholder="Ej.: 50 mg"></div>
        </div>
        <label for="md-horas">Horas de toma <span class="ayuda">Le recordaremos a esas horas. Separe con comas, ej.: 08:00, 20:00</span></label>
        <input id="md-horas" placeholder="08:00">
        <div class="fila-botones"><button class="btn" type="submit">Agregar medicamento</button></div>
      </form></details>
  </section>

  <section class="bloque"><h2>Mis recordatorios</h2>
    ${recs.length ? `<ul class="lista">${recs.sort((a, b) => a.hora.localeCompare(b.hora)).map((r) => `<li>
        <span><span class="principal">${r.hora}</span> <span class="etiqueta">${TIPOS_RECORDATORIO[r.tipo]}</span><br>
        <span class="sec">${esc(r.titulo)}${r.fecha ? ` (${fechaLarga(r.fecha + "T12:00")})` : ""}</span></span>
        <button class="boton-texto rojo" data-rec="${r.id}">Quitar</button></li>`).join("")}</ul>`
      : `<p class="vacio">No tiene recordatorios activos.</p>`}
    <details><summary>Agregar una cita médica</summary>
      <form id="form-cita">
        <label for="ci-tit">Motivo</label><input id="ci-tit" required placeholder="Ej.: Control con cardiología">
        <div class="dos-col">
          <div><label for="ci-fecha">Fecha</label><input id="ci-fecha" type="date" required></div>
          <div><label for="ci-hora">Hora del aviso</label><input id="ci-hora" type="time" value="07:00" required></div>
        </div>
        <div class="fila-botones"><button class="btn" type="submit">Agregar cita</button></div>
      </form></details>
  </section>

  <section class="bloque"><h2>Mis datos de salud</h2>
    <form id="form-perfil">
      <div class="dos-col">
        <div><label for="p-sh">Presión habitual: número de arriba</label><input id="p-sh" type="number" min="60" max="260" value="${v(p.sistolica_habitual)}"></div>
        <div><label for="p-dh">Presión habitual: número de abajo</label><input id="p-dh" type="number" min="30" max="160" value="${v(p.diastolica_habitual)}"></div>
      </div>
      <p class="nota" style="margin-top:1rem">Su meta, definida con su médico. Si no la conoce, deje los valores recomendados.</p>
      <div class="dos-col">
        <div><label for="p-ms">Meta: número de arriba máximo</label><input id="p-ms" type="number" min="100" max="170" value="${p.meta_sistolica_max}"></div>
        <div><label for="p-md">Meta: número de abajo máximo</label><input id="p-md" type="number" min="60" max="100" value="${p.meta_diastolica_max}"></div>
      </div>
      <label for="p-fr">Otras condiciones <span class="ayuda">Ej.: diabetes, colesterol alto, fumador. Separe con comas.</span></label>
      <input id="p-fr" value="${esc(p.factores_riesgo.join(", "))}">
      <label for="p-ant">Antecedentes importantes</label><textarea id="p-ant" rows="2">${esc(v(p.antecedentes))}</textarea>
      <label for="p-med">Médico tratante</label><input id="p-med" value="${esc(v(p.medico_tratante))}">
      <div class="fila-botones"><button class="btn" type="submit">Guardar cambios</button></div>
    </form>
  </section>

  <section class="bloque"><h2>Tamaño del texto</h2>
    <div class="fila-botones" style="margin-top:0" role="group" aria-label="Tamaño del texto">
      <button class="btn secundario" data-tam="normal">Normal</button>
      <button class="btn secundario" data-tam="grande" style="font-size:1.12em">Grande</button>
      <button class="btn secundario" data-tam="muy-grande" style="font-size:1.25em">Muy grande</button>
    </div>
  </section>

  <section class="bloque"><h2>Privacidad</h2>
    <p>Sus datos se guardan cifrados. Solo usted decide con quién compartirlos.</p>
    <div class="fila-botones">
      <button class="btn secundario" id="exportar">Descargar todos mis datos</button>
      <button class="btn secundario" id="salir">Cerrar sesión</button>
      <button class="btn peligro" id="borrar">Eliminar mi cuenta</button>
    </div>
  </section>`;

  c.querySelectorAll("[data-med]").forEach((b) => (b.onclick = async () => {
    if (!confirm("¿Dejar de registrar este medicamento? También se quitarán sus recordatorios.")) return;
    await api(`/perfil/medicamentos/${b.dataset.med}`, { metodo: "DELETE" });
    toast("Medicamento quitado.");
    irA("perfil");
  }));
  c.querySelectorAll("[data-rec]").forEach((b) => (b.onclick = async () => {
    await api(`/recordatorios/${b.dataset.rec}`, { metodo: "DELETE" });
    toast("Recordatorio quitado.");
    irA("perfil");
  }));
  c.querySelectorAll("[data-tam]").forEach((b) => (b.onclick = () => {
    cambiarTamTexto(b.dataset.tam);
    toast("Tamaño del texto actualizado.");
  }));

  $("#form-med").onsubmit = async (e) => {
    e.preventDefault();
    const horas = $("#md-horas").value.split(",").map((h) => h.trim()).filter(Boolean).map((h) => (h.length === 4 ? "0" + h : h));
    try {
      await api("/perfil/medicamentos", { metodo: "POST", json: {
        nombre: $("#md-nom").value.trim(), dosis: $("#md-dosis").value.trim() || null, horarios: horas } });
      toast("Medicamento agregado.");
      irA("perfil");
    } catch (err) { toast(err.message.includes("Hora") ? err.message : "Revise las horas: use el formato 08:00 o 20:30."); }
  };

  $("#form-cita").onsubmit = async (e) => {
    e.preventDefault();
    try {
      await api("/recordatorios", { metodo: "POST", json: {
        tipo: "cita", titulo: $("#ci-tit").value.trim(), fecha: $("#ci-fecha").value, hora: $("#ci-hora").value } });
      toast("Cita agregada.");
      irA("perfil");
    } catch (err) { toast(err.message); }
  };

  $("#form-perfil").onsubmit = async (e) => {
    e.preventDefault();
    const num = (id) => ($(id).value ? +$(id).value : null);
    const metaMax = num("#p-ms") ?? 129;
    try {
      await api("/perfil", { metodo: "PUT", json: {
        sistolica_habitual: num("#p-sh"), diastolica_habitual: num("#p-dh"),
        meta_sistolica_min: Math.min(p.meta_sistolica_min, metaMax), meta_sistolica_max: metaMax,
        meta_diastolica_max: num("#p-md") ?? 79,
        factores_riesgo: $("#p-fr").value.split(",").map((x) => x.trim()).filter(Boolean),
        antecedentes: $("#p-ant").value.trim() || null, medico_tratante: $("#p-med").value.trim() || null } });
      toast("Cambios guardados.");
    } catch (err) { toast(err.message); }
  };

  $("#exportar").onclick = async () => {
    const datos = await api("/privacidad/exportar");
    descargar(new Blob([JSON.stringify(datos, null, 2)], { type: "application/json" }), "mis_datos.json");
  };
  $("#salir").onclick = cerrarSesion;
  $("#borrar").onclick = async () => {
    if (!confirm("¿Eliminar su cuenta y TODAS sus mediciones? Esta acción no se puede deshacer.")) return;
    await api("/privacidad/cuenta", { metodo: "DELETE" });
    cerrarSesion();
    toast("Su cuenta fue eliminada.");
  };
}

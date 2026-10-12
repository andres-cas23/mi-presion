// =========================================================
// VISTA: MEDICIONES (tensiómetros, historial y registro manual)
// =========================================================
import { api } from "../api/cliente.js";
import { conectarTensiometro, enviarPaquetes, paqueteSimulado } from "../servicios/bluetooth.js";
import { $, esc, toast } from "../utils/dom.js";
import { CATEGORIAS, CONTEXTOS, cuando, fechaLarga, fechaLocalISO, FUENTES, hora } from "../utils/formato.js";
import { irA } from "../utils/navegar.js";

export async function mostrar(c) {
  const [dispositivos, lecturas] = await Promise.all([api("/dispositivos"), api("/lecturas")]);

  c.innerHTML = `
    <div class="encabezado"><h1>Mediciones</h1><p>Sus datos llegan solos desde el tensiómetro</p></div>
    <section class="bloque"><h2>Mis tensiómetros</h2>
      ${dispositivos.length ? "" : "<p>Registre su tensiómetro una sola vez. Después, cada medición se guardará sola.</p>"}
      ${dispositivos.map(tarjetaDispositivo).join("")}
      ${formularioDispositivo(dispositivos.length === 0)}
    </section>
    <section class="bloque"><h2>Historial</h2>${historial(lecturas)}</section>
    <section class="bloque">${formularioManual()}</section>`;

  // Botones de cada tensiómetro
  c.querySelectorAll("[data-ble]").forEach((b) => (b.onclick = () => {
    const estado = $(`#estado-${b.dataset.ble}`);
    estado.hidden = false;
    conectarTensiometro(b.dataset.ble, (texto) => (estado.textContent = texto));
  }));
  c.querySelectorAll("[data-simular]").forEach((b) => (b.onclick = () =>
    simular(b.dataset.simular, b.dataset.tipo === "crisis").catch((e) => toast(e.message))));

  $("#form-disp").onsubmit = async (e) => {
    e.preventDefault();
    try {
      await api("/dispositivos", { metodo: "POST", json: {
        fabricante: $("#d-fab").value, modelo: $("#d-mod").value.trim(), fecha_compra: $("#d-compra").value || null } });
      toast("Tensiómetro agregado.");
      irA("mediciones");
    } catch (err) { toast(err.message); }
  };

  $("#form-manual").onsubmit = async (e) => {
    e.preventDefault();
    const sis = +$("#m-sis").value, dia = +$("#m-dia").value;
    if (sis <= dia) return toast("El número de arriba debe ser mayor que el de abajo.");
    try {
      const r = await api("/lecturas/manual", { metodo: "POST", json: {
        sistolica: sis, diastolica: dia, pulso: $("#m-pul").value ? +$("#m-pul").value : null,
        medido_en: $("#m-fecha").value + ":00", contexto: $("#m-ctx").value || null, notas: $("#m-notas").value || null } });
      toast(r.alerta ? "Medición guardada. Atención: su presión está muy alta." : "Medición guardada.");
      irA("inicio");
    } catch (err) { toast(err.message); }
  };
}

async function simular(dispositivoId, crisis) {
  const estado = $(`#estado-${dispositivoId}`);
  estado.hidden = false;
  estado.textContent = "El tensiómetro está enviando la medición…";
  const azar = (n) => Math.round(Math.random() * n);
  const sis = crisis ? 184 + azar(8) : 122 + azar(22);
  const dia = crisis ? 112 + azar(6) : Math.round(sis * 0.62 + azar(6));
  const { mensaje } = await enviarPaquetes(dispositivoId, [{ payload_hex: paqueteSimulado(sis, dia, 62 + azar(20)) }]);
  estado.textContent = mensaje;
  toast(mensaje);
  setTimeout(() => irA("inicio"), 1400);
}

const tarjetaDispositivo = (d) => `<div class="dispositivo">
  <h3>${esc(d.fabricante)} ${esc(d.modelo)}</h3>
  <div class="nota">${d.ultima_sincronizacion ? `Última sincronización: ${cuando(d.ultima_sincronizacion)}` : "Aún no se ha sincronizado"}</div>
  ${d.aviso_calibracion ? `<div class="aviso advertencia" style="margin:.8rem 0 0">${esc(d.aviso_calibracion)}</div>` : ""}
  <div class="fila-botones">
    <button class="btn" data-ble="${d.id}">Sincronizar por Bluetooth</button>
    <button class="btn secundario" data-simular="${d.id}">Simular medición</button>
    <button class="btn secundario" data-simular="${d.id}" data-tipo="crisis">Simular presión muy alta</button>
  </div>
  <div class="estado-ble" id="estado-${d.id}" role="status" hidden></div>
</div>`;

const formularioDispositivo = (abierto) => `<details ${abierto ? "open" : ""}><summary>Agregar un tensiómetro</summary>
  <form id="form-disp">
    <div class="dos-col">
      <div><label for="d-fab">Marca</label><select id="d-fab"><option>Omron</option><option>Withings</option><option>Qardio</option><option>A&amp;D</option><option>Beurer</option><option>Otra</option></select></div>
      <div><label for="d-mod">Modelo</label><input id="d-mod" required placeholder="Ej.: HEM-7155T"></div>
    </div>
    <label for="d-compra">Fecha de compra <span class="ayuda">Opcional. Le avisaremos si el equipo necesita revisión.</span></label>
    <input id="d-compra" type="date">
    <div class="fila-botones"><button class="btn" type="submit">Agregar tensiómetro</button></div>
  </form></details>`;

function historial(lecturas) {
  if (!lecturas.length) return `<p class="vacio">Todavía no hay mediciones.</p>`;
  let html = "", diaActual = "";
  for (const l of [...lecturas].reverse().slice(0, 120)) {
    const dia = new Date(l.medido_en).toDateString();
    if (dia !== diaActual) {
      html += `${diaActual ? "</ul>" : ""}<div class="dia-titulo">${fechaLarga(l.medido_en)}</div><ul class="lista">`;
      diaActual = dia;
    }
    const cat = CATEGORIAS[l.categoria];
    const fuente = l.fuente === "manual" ? "Manual" : l.fuente === "bluetooth" ? "Bluetooth" : FUENTES[l.fuente];
    html += `<li class="lectura-fila">
      <span class="sec">${hora(l.medido_en)}</span>
      <span class="valor-lectura"><span class="punto" style="background:${cat.color}"></span>${l.sistolica}/${l.diastolica}</span>
      <span class="sec sec-extra">${cat.nombre}${l.pulso ? `, pulso ${l.pulso}` : ""}${CONTEXTOS[l.contexto] ? `. ${CONTEXTOS[l.contexto]}` : ""}${l.pulso_irregular ? ". <b style='color:var(--rojo)'>Pulso irregular</b>" : ""}</span>
      <span class="etiqueta">${fuente}</span>
    </li>`;
  }
  return html + "</ul>";
}

const formularioManual = () => `<details style="border:0;margin:0;padding:0"><summary>¿No pudo sincronizar? Escriba la medición a mano</summary>
  <form id="form-manual">
    <div class="dos-col">
      <div><label for="m-sis">Número de arriba <span class="ayuda">Sistólica</span></label><input id="m-sis" type="number" inputmode="numeric" min="50" max="300" required></div>
      <div><label for="m-dia">Número de abajo <span class="ayuda">Diastólica</span></label><input id="m-dia" type="number" inputmode="numeric" min="30" max="200" required></div>
      <div><label for="m-pul">Pulso <span class="ayuda">Opcional</span></label><input id="m-pul" type="number" inputmode="numeric" min="25" max="250"></div>
      <div><label for="m-fecha">Fecha y hora</label><input id="m-fecha" type="datetime-local" value="${fechaLocalISO(new Date())}" required></div>
    </div>
    <label for="m-ctx">¿Cuándo midió?</label>
    <select id="m-ctx"><option value="">Que la aplicación lo calcule según mis medicamentos</option>
      ${Object.entries(CONTEXTOS).filter(([k]) => k !== "sin_especificar").map(([k, v]) => `<option value="${k}">${v}</option>`).join("")}</select>
    <label for="m-notas">Notas <span class="ayuda">Opcional</span></label><input id="m-notas" maxlength="500">
    <div class="fila-botones"><button class="btn" type="submit">Guardar medición</button></div>
  </form></details>`;

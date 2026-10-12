// =========================================================
// VISTA: ASISTENTE (preguntas sobre hipertensión con Gemini)
//
// La llave de Gemini NO está aquí: vive en el servidor. El
// navegador solo envía la pregunta al backend (/asistente/preguntar).
// =========================================================
import { api } from "../api/cliente.js";
import { textoEnriquecido } from "../componentes/texto_enriquecido.js";
import { $, esc, toast } from "../utils/dom.js";

const CLAVE = "mi-presion-chat";
const SUGERENCIAS = [
  "¿Qué alimentos debo evitar si tengo la presión alta?",
  "¿Cómo me mido bien la presión en casa?",
  "¿Cómo va mi presión esta semana?",
  "¿Puedo tomar café?",
  "¿Qué ejercicio me recomienda?",
];

// La conversación se guarda solo en esta pestaña del navegador.
const cargarHistorial = () => { try { return JSON.parse(sessionStorage.getItem(CLAVE)) || []; } catch { return []; } };
const guardarHistorial = (h) => sessionStorage.setItem(CLAVE, JSON.stringify(h.slice(-20)));

export async function mostrar(c) {
  const estado = await api("/asistente/estado");
  let historial = cargarHistorial();

  c.innerHTML = `
    <div class="encabezado"><h1>Asistente</h1><p>Pregunte sobre la presión arterial</p></div>
    ${estado.configurado ? "" : `<div class="aviso advertencia"><strong>El asistente aún no está activado</strong>
      El administrador debe configurar la llave de Gemini (GEMINI_API_KEY) en el servidor.</div>`}
    <div class="aviso info">Este asistente da información educativa y <b>no reemplaza a su médico</b>.
      Ante dolor en el pecho, falta de aire o una presión de 180/120 o más, llame al <b>123</b>.</div>
    <div class="chat" id="chat" aria-live="polite"></div>
    <div id="zona-sugerencias"></div>
    <form class="caja-pregunta" id="form-pregunta">
      <label for="pregunta" class="nota" style="margin-top:0">Escriba su pregunta</label>
      <textarea id="pregunta" maxlength="1000" required placeholder="Ej.: ¿Por qué me sube la presión en la mañana?"></textarea>
      <label class="check" style="margin-top:.6rem"><input type="checkbox" id="usar-datos" checked>
        <span>Usar mis mediciones para darme una respuesta personalizada</span></label>
      <div class="fila-botones" style="margin-top:.6rem">
        <button class="btn" type="submit" ${estado.configurado ? "" : "disabled"}>Preguntar</button>
        <button class="btn secundario" type="button" id="nueva">Nueva conversación</button>
      </div>
    </form>`;

  const chat = $("#chat");
  const pintar = () => {
    chat.innerHTML = historial.map((m) => m.rol === "usuario"
      ? `<div class="msg usuario">${esc(m.texto)}</div>`
      : `<div class="msg asistente ${m.urgente ? "urgente" : ""}">${textoEnriquecido(m.texto)}</div>`).join("");
    $("#zona-sugerencias").innerHTML = historial.length ? "" :
      `<p class="nota">Puede empezar con una de estas preguntas:</p>
       <div class="sugerencias">${SUGERENCIAS.map((s) => `<button type="button">${esc(s)}</button>`).join("")}</div>`;
    $("#zona-sugerencias").querySelectorAll("button").forEach((b) => (b.onclick = () => preguntar(b.textContent)));
  };

  async function preguntar(texto) {
    if (!estado.configurado) return toast("El asistente aún no está activado.");
    const boton = $("#form-pregunta button[type=submit]");
    boton.disabled = true;
    const anteriores = historial.map(({ rol, texto }) => ({ rol, texto }));
    historial.push({ rol: "usuario", texto });
    pintar();
    chat.insertAdjacentHTML("beforeend", `<div class="msg asistente pensando" id="pensando">Escribiendo respuesta…</div>`);
    $("#pensando").scrollIntoView({ behavior: "smooth", block: "end" });
    try {
      const r = await api("/asistente/preguntar", { metodo: "POST", json: {
        pregunta: texto, historial: anteriores.slice(-10), usar_mis_datos: $("#usar-datos").checked } });
      historial.push({ rol: "asistente", texto: r.respuesta, urgente: r.urgente });
    } catch (err) {
      historial.pop();                 // quita la pregunta que no se pudo responder
      $("#pregunta").value = texto;    // y la devuelve a la caja para reintentar
      toast(err.message);
    }
    guardarHistorial(historial);
    pintar();
    boton.disabled = false;
    chat.lastElementChild?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  $("#form-pregunta").onsubmit = (e) => {
    e.preventDefault();
    const texto = $("#pregunta").value.trim();
    if (texto.length < 2) return;
    $("#pregunta").value = "";
    preguntar(texto);
  };
  $("#pregunta").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#form-pregunta").requestSubmit(); }
  });
  $("#nueva").onclick = () => { historial = []; guardarHistorial(historial); pintar(); };

  pintar();
}

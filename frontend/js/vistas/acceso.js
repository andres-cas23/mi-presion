// =========================================================
// VISTA: ACCESO (entrar o crear cuenta)
// =========================================================
import { api } from "../api/cliente.js";
import { crearCuenta, iniciarSesion } from "../servicios/sesion.js";
import { $, esc, toast } from "../utils/dom.js";

const LOGO = `<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1D5C96" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z"/><path d="M3.5 12h4l2-3 3 6 2-3h6"/></svg>`;

/** @param alEntrar función que se ejecuta cuando la persona inicia sesión */
export function mostrar(contenedor, alEntrar) {
  contenedor.innerHTML = `<div class="bloque">
    <div class="marca">${LOGO} Mi Presión</div>
    <p class="nota">Su presión arterial, registrada sola desde su tensiómetro.</p>
    <div class="pestanas" role="tablist">
      <button role="tab" id="tab-entrar" aria-selected="true">Entrar</button>
      <button role="tab" id="tab-crear" aria-selected="false">Crear cuenta</button>
    </div>
    <div id="aviso-acceso" role="alert"></div>

    <form id="form-entrar">
      <label for="e-email">Correo</label>
      <input id="e-email" type="email" autocomplete="username" required>
      <label for="e-pass">Contraseña</label>
      <input id="e-pass" type="password" autocomplete="current-password" required>
      <div class="fila-botones"><button class="btn" type="submit">Entrar</button></div>
    </form>

    <form id="form-crear" hidden>
      <label for="c-nombre">Su nombre</label>
      <input id="c-nombre" autocomplete="name" required minlength="2">
      <label for="c-nac">Fecha de nacimiento</label>
      <input id="c-nac" type="date">
      <label for="c-email">Correo</label>
      <input id="c-email" type="email" autocomplete="username" required>
      <label for="c-pass">Contraseña <span class="ayuda">Mínimo 8 caracteres</span></label>
      <input id="c-pass" type="password" autocomplete="new-password" required minlength="8">
      <label class="check" style="margin-top:1.2rem">
        <input id="c-consent" type="checkbox" required>
        <span>Autorizo el tratamiento de mis datos de salud para el seguimiento de mi presión arterial, según la Ley 1581 de 2012.
          <button type="button" class="boton-texto" id="ver-politica">Leer la política</button></span>
      </label>
      <div id="politica" class="aviso info" hidden></div>
      <div class="fila-botones"><button class="btn" type="submit">Crear cuenta</button></div>
    </form>
  </div>`;

  const aviso = (msg) => ($("#aviso-acceso").innerHTML = `<div class="aviso urgente">${esc(msg)}</div>`);
  const pestana = (crear) => {
    $("#tab-entrar").setAttribute("aria-selected", !crear);
    $("#tab-crear").setAttribute("aria-selected", crear);
    $("#form-entrar").hidden = crear;
    $("#form-crear").hidden = !crear;
    $("#aviso-acceso").innerHTML = "";
  };
  $("#tab-entrar").onclick = () => pestana(false);
  $("#tab-crear").onclick = () => pestana(true);

  $("#ver-politica").onclick = async () => {
    const caja = $("#politica");
    if (!caja.hidden) return (caja.hidden = true);
    try {
      const pol = await api("/privacidad/politica");
      caja.innerHTML = `<ul style="margin:0;padding-left:1.1em">${pol.resumen.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
        <p class="nota" style="margin:.5rem 0 0">${esc(pol.marco_legal)}</p>`;
      caja.hidden = false;
    } catch (err) { aviso(err.message); }
  };

  const conBoton = async (form, accion) => {
    const boton = form.querySelector("button[type=submit]");
    boton.disabled = true;
    try { await accion(); } catch (err) { aviso(err.message); }
    boton.disabled = false;
  };

  $("#form-entrar").onsubmit = (e) => {
    e.preventDefault();
    conBoton(e.target, async () => {
      await iniciarSesion($("#e-email").value.trim(), $("#e-pass").value);
      alEntrar();
    });
  };

  $("#form-crear").onsubmit = (e) => {
    e.preventDefault();
    conBoton(e.target, async () => {
      await crearCuenta({
        nombre: $("#c-nombre").value.trim(), email: $("#c-email").value.trim(), password: $("#c-pass").value,
        fecha_nacimiento: $("#c-nac").value || null, acepta_tratamiento_datos: $("#c-consent").checked,
      });
      alEntrar();
      toast("Cuenta creada. Le programamos recordatorios para medir en la mañana y en la noche.");
    });
  };
}

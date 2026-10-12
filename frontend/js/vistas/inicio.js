// =========================================================
// VISTA: INICIO (última medición, semana, gráfico, recordatorios)
// =========================================================
import { api } from "../api/cliente.js";
import { animarEscalas, escala, leyendaEscala } from "../componentes/escala.js";
import { grafico } from "../componentes/grafico.js";
import { usuario } from "../servicios/sesion.js";
import { esc } from "../utils/dom.js";
import { CATEGORIAS, cuando, fechaLarga, fechaLocalISO, FUENTES, hora, MENSAJES } from "../utils/formato.js";
import { irA } from "../utils/navegar.js";

export async function mostrar(c) {
  const hace30dias = fechaLocalISO(Date.now() - 30 * 864e5);
  const [lecturas, hbpm, alertas, proximos] = await Promise.all([
    api(`/lecturas?desde=${hace30dias}`), api("/lecturas/hbpm"), api("/alertas"), api("/recordatorios/proximos?horas=24"),
  ]);
  const ultima = lecturas.at(-1);
  const h = new Date().getHours();
  const saludo = h >= 5 && h < 12 ? "Buenos días" : h >= 12 && h < 19 ? "Buenas tardes" : "Buenas noches";

  c.innerHTML = `
    <div class="encabezado"><h1>${saludo}, ${esc(usuario()?.nombre.split(" ")[0] ?? "")}</h1><p>${fechaLarga(new Date())}</p></div>
    ${alertas.map(tarjetaAlerta).join("")}
    ${ultima ? tarjetaUltima(ultima) : tarjetaSinDatos()}
    ${tarjetaSemana(hbpm)}
    <section class="bloque"><h2>Últimos 30 días</h2>${grafico(lecturas)}</section>
    ${tarjetaRecordatorios(proximos)}`;

  animarEscalas(c);
  c.querySelectorAll("[data-atender]").forEach((b) => (b.onclick = async () => {
    await api(`/alertas/${b.dataset.atender}/atender`, { metodo: "POST" });
    irA("inicio");
  }));
}

const tarjetaAlerta = (a) => `<div class="aviso ${a.nivel}" role="alert">
  <strong>${a.nivel === "urgente" ? "Atención: presión muy alta" : "Aviso"} (${cuando(a.creada_en)})</strong>${esc(a.mensaje)}
  <div class="fila-botones"><button class="btn secundario" data-atender="${a.id}">Entendido</button></div></div>`;

const tarjetaSinDatos = () => `<section class="bloque lectura-hero"><h2>Aún no tiene mediciones</h2>
  <p>Conecte su tensiómetro y sus mediciones aparecerán aquí solas, sin tener que escribirlas.</p>
  <div class="fila-botones"><a class="btn" href="#/mediciones">Conectar mi tensiómetro</a></div></section>`;

function tarjetaUltima(l) {
  return `<section class="bloque lectura-hero" aria-labelledby="t-ultima">
    <h2 id="t-ultima" class="cuando">Su última medición: ${cuando(l.medido_en)}, desde ${FUENTES[l.fuente]}</h2>
    <div class="cifra"><span class="num">${l.sistolica}</span><span class="barra">/</span><span class="num">${l.diastolica}</span><span class="unidad">mmHg</span></div>
    ${l.pulso ? `<div class="pulso">Pulso: ${l.pulso} latidos por minuto${l.pulso_irregular ? `. <b style="color:var(--rojo)">El tensiómetro detectó pulso irregular</b>` : ""}</div>` : ""}
    <span class="categoria cat-${l.categoria}">${CATEGORIAS[l.categoria].nombre}</span>
    <p>${MENSAJES[l.categoria]}</p>
    <div class="escalas">
      ${escala(l.sistolica, 90, 200, [120, 140, 180], "Número de arriba", "sistólica")}
      ${escala(l.diastolica, 50, 130, [70, 90, 120], "Número de abajo", "diastólica")}
    </div>
    ${leyendaEscala}
  </section>`;
}

function tarjetaSemana(hbpm) {
  const porFecha = Object.fromEntries(hbpm.detalle_por_dia.map((d) => [d.fecha, d]));
  let barras = "";
  for (let i = 6; i >= 0; i--) {
    const d = porFecha[fechaLocalISO(Date.now() - i * 864e5).slice(0, 10)];
    const clase = d && d.lecturas_manana && d.lecturas_noche ? "lleno" : d ? "medio" : "";
    barras += `<span class="${clase}" title="${d ? `${d.lecturas_manana} en la mañana, ${d.lecturas_noche} en la noche` : "Sin mediciones"}"></span>`;
  }
  const promedio = hbpm.promedio_sistolica != null
    ? `${Math.round(hbpm.promedio_sistolica)}/${Math.round(hbpm.promedio_diastolica)}` : "Sin datos";
  const tipo = hbpm.supera_umbral_domiciliario ? "advertencia" : hbpm.protocolo_minimo_cumplido ? "ok" : "info";
  return `<section class="bloque"><h2>Su semana</h2>
    <p class="nota" style="margin-bottom:.2rem">Días con mediciones en la mañana y en la noche (últimos 7 días)</p>
    <div class="progreso-dias" aria-label="${hbpm.dias_completos} de 7 días completos">${barras}</div>
    <div class="resumen">
      <div><b>${promedio}</b><span>Promedio en casa</span></div>
      <div><b>${hbpm.dias_completos} de 7</b><span>Días completos</span></div>
      <div><b>${hbpm.total_lecturas}</b><span>Mediciones</span></div>
    </div>
    <div class="aviso ${tipo}" style="margin:0">${esc(hbpm.interpretacion)}</div>
  </section>`;
}

function tarjetaRecordatorios(proximos) {
  if (!proximos.length) return `<section class="bloque"><h2>Próximos recordatorios</h2><p class="vacio">No tiene recordatorios en las próximas 24 horas.</p></section>`;
  const filas = proximos.slice(0, 5).map((p) => `<li>
      <span><span class="principal">${hora(p.programado_para)}</span> <span class="sec">${cuando(p.programado_para).startsWith("Hoy") ? "hoy" : "mañana"}</span></span>
      <span style="flex:2;min-width:12em">${esc(p.recordatorio.titulo)}</span></li>`).join("");
  return `<section class="bloque"><h2>Próximos recordatorios</h2><ul class="lista">${filas}</ul></section>`;
}

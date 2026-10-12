// Textos y formatos que se repiten en varias pantallas.

export const CATEGORIAS = {
  no_elevada: { nombre: "No elevada", color: "var(--verde)" },
  elevada: { nombre: "Elevada", color: "var(--ambar)" },
  hipertension: { nombre: "Hipertensión", color: "var(--naranja)" },
  crisis_hipertensiva: { nombre: "Muy alta: crisis", color: "var(--rojo)" },
};

export const MENSAJES = {
  no_elevada: "Su presión está en un rango no elevado. ¡Siga así!",
  elevada: "Su presión está elevada. Mantenga sus hábitos saludables y siga midiendo según su plan.",
  hipertension: "Su presión está en rango de hipertensión. Si se repite, compártalo con su médico.",
  crisis_hipertensiva: "Su presión está muy alta. Siéntese, descanse 5 minutos y vuelva a medir. Si sigue igual o tiene dolor en el pecho, falta de aire o dolor de cabeza fuerte, llame al 123.",
};

export const FUENTES = {
  bluetooth: "su tensiómetro", manual: "registro manual", apple_health: "Apple Health",
  google_fit: "Google Fit", samsung_health: "Samsung Health",
};

export const CONTEXTOS = {
  antes_medicacion: "Antes del medicamento", despues_medicacion: "Después del medicamento",
  antes_actividad: "Antes de actividad física", despues_actividad: "Después de actividad física",
  reposo: "En reposo", sin_especificar: "",
};

export const TIPOS_RECORDATORIO = { medicion: "Medir la presión", medicamento: "Medicamento", cita: "Cita médica" };

export const fechaLarga = (d) =>
  new Date(d).toLocaleDateString("es-CO", { weekday: "long", day: "numeric", month: "long" });

export const hora = (d) => new Date(d).toLocaleTimeString("es-CO", { hour: "numeric", minute: "2-digit" });

/** "Hoy a las 7:10 a. m.", "Ayer a las...", o la fecha completa. */
export function cuando(d) {
  const f = new Date(d), hoy = new Date(), ayer = new Date(Date.now() - 864e5);
  const mismoDia = (a, b) => a.toDateString() === b.toDateString();
  if (mismoDia(f, hoy)) return `Hoy a las ${hora(f)}`;
  if (mismoDia(f, ayer)) return `Ayer a las ${hora(f)}`;
  return `${fechaLarga(f)}, ${hora(f)}`;
}

/** Fecha en formato local "AAAA-MM-DDTHH:MM" (para inputs y para la API). */
export function fechaLocalISO(d) {
  const x = new Date(d);
  x.setMinutes(x.getMinutes() - x.getTimezoneOffset());
  return x.toISOString().slice(0, 16);
}

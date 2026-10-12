// =========================================================
// BLUETOOTH: conexión con tensiómetros reales (Web Bluetooth)
// y simulación de un paquete Bluetooth para pruebas.
//
// Usa el perfil estándar de presión arterial (servicio 0x1810,
// característica 0x2A35). Los bytes se envían tal cual al backend,
// que los decodifica en app/services/ble_parser.py.
// =========================================================
import { api } from "../api/cliente.js";

const aHex = (bytes) => [...bytes].map((x) => x.toString(16).padStart(2, "0")).join("");

export const bluetoothDisponible = () => Boolean(navigator.bluetooth);

/** Envía paquetes al backend y devuelve un mensaje para el usuario. */
export async function enviarPaquetes(dispositivoId, paquetes) {
  const r = await api(`/dispositivos/${dispositivoId}/sincronizar-ble`, { metodo: "POST", json: { paquetes } });
  let msg = r.nuevas ? `Se recibieron ${r.nuevas} medición(es) nueva(s).` : "No había mediciones nuevas.";
  if (r.duplicadas) msg += ` ${r.duplicadas} ya estaban guardadas.`;
  if (r.alertas.length) msg += " Hay una alerta: revise la pantalla de inicio.";
  return { resultado: r, mensaje: msg };
}

/**
 * Conecta con un tensiómetro real. `alCambiarEstado(texto)` informa el avance.
 * Las mediciones se agrupan y se envían 2,5 s después de la última recibida.
 */
export async function conectarTensiometro(dispositivoId, alCambiarEstado) {
  if (!bluetoothDisponible()) {
    alCambiarEstado("Este navegador no permite Bluetooth. Use Google Chrome o Microsoft Edge en computador o Android. Mientras tanto, puede usar «Simular medición».");
    return;
  }
  try {
    alCambiarEstado("Encienda su tensiómetro y presione su botón de Bluetooth. Luego elija el equipo en la ventana que aparece.");
    const equipo = await navigator.bluetooth.requestDevice({ filters: [{ services: ["blood_pressure"] }] });
    alCambiarEstado(`Conectando con ${equipo.name || "el tensiómetro"}…`);
    const servidor = await equipo.gatt.connect();
    const servicio = await servidor.getPrimaryService("blood_pressure");
    const medicion = await servicio.getCharacteristic("blood_pressure_measurement");

    const pendientes = [];
    let temporizador;
    medicion.addEventListener("characteristicvaluechanged", (e) => {
      const v = e.target.value;
      pendientes.push({ payload_hex: aHex(new Uint8Array(v.buffer, v.byteOffset, v.byteLength)), recibido_en: new Date().toISOString() });
      alCambiarEstado(`Recibiendo mediciones… (${pendientes.length})`);
      clearTimeout(temporizador);
      temporizador = setTimeout(async () => {
        const { mensaje } = await enviarPaquetes(dispositivoId, pendientes.splice(0));
        alCambiarEstado(mensaje);
      }, 2500);
    });
    await medicion.startNotifications();
    alCambiarEstado("Conectado. Tome su medición o espere a que el tensiómetro envíe las guardadas en su memoria.");
  } catch (err) {
    alCambiarEstado(err.name === "NotFoundError" ? "No se eligió ningún tensiómetro." : `No se pudo conectar: ${err.message}`);
  }
}

/** Crea un paquete Bluetooth 0x2A35 idéntico al de un tensiómetro real (para pruebas). */
export function paqueteSimulado(sistolica, diastolica, pulso, fecha = new Date()) {
  const b = [0x16]; // banderas: incluye fecha, pulso y estado
  const u16 = (v) => b.push(v & 0xff, (v >> 8) & 0xff);
  u16(sistolica & 0x0fff);
  u16(diastolica & 0x0fff);
  u16(Math.round(diastolica + (sistolica - diastolica) / 3) & 0x0fff);
  u16(fecha.getFullYear());
  b.push(fecha.getMonth() + 1, fecha.getDate(), fecha.getHours(), fecha.getMinutes(), fecha.getSeconds());
  u16(pulso & 0x0fff);
  u16(0);
  return aHex(b);
}

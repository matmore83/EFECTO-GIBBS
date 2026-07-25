const estado = {
  tipo: "pulso",
  frecuencia: 5,
  amplitud: 1,
  armonicos: 5,
  fs: 20000,
  periodos: 3,
  tolerancia: 0.001,
};

const el = (id) => document.getElementById(id);

const COLOR_IDEAL = "rgba(139, 147, 167, 0.7)";
const COLOR_FOURIER = "#7c5cff";
const COLOR_ERROR = "#ff5c93";
const COLOR_ESPECTRO = "#22d3c8";
const COLOR_AUDIO = "#22d3c8";

Chart.defaults.color = "#8b93a7";
Chart.defaults.borderColor = "rgba(255,255,255,0.06)";
Chart.defaults.font.family = "Segoe UI, system-ui, sans-serif";

function crearGraficoLinea(ctx, datasets, opciones = {}) {
  return new Chart(ctx, {
    type: "line",
    data: { labels: [], datasets },
    options: {
      animation: false,
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "nearest", intersect: false },
      elements: { point: { radius: 0 } },
      scales: {
        x: { ticks: { maxTicksLimit: 8 }, grid: { color: "rgba(255,255,255,0.04)" } },
        y: { grid: { color: "rgba(255,255,255,0.04)" } },
      },
      plugins: { legend: { labels: { boxWidth: 12 } } },
      ...opciones,
    },
  });
}

const graficoSenal = crearGraficoLinea(el("grafico-senal"), [
  { label: "Señal ideal", data: [], borderColor: COLOR_IDEAL, borderWidth: 1.5, borderDash: [4, 3] },
  { label: "Serie de Fourier", data: [], borderColor: COLOR_FOURIER, borderWidth: 2 },
]);

const graficoError = crearGraficoLinea(el("grafico-error"), [
  { label: "Error %", data: [], borderColor: COLOR_ERROR, borderWidth: 1.5, fill: true, backgroundColor: "rgba(255,92,147,0.12)" },
]);

const graficoEspectro = new Chart(el("grafico-espectro"), {
  type: "bar",
  data: { labels: [], datasets: [{ label: "Magnitud", data: [], backgroundColor: COLOR_ESPECTRO, borderRadius: 4 }] },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: "rgba(255,255,255,0.04)" } },
    },
    plugins: { legend: { display: false } },
  },
});

const graficoAudio = crearGraficoLinea(el("grafico-audio"), [
  { label: "Audio importado", data: [], borderColor: COLOR_AUDIO, borderWidth: 1.2 },
]);

function redondear(valor, decimales = 3) {
  return Number(valor).toFixed(decimales);
}

async function obtenerJSON(url) {
  const respuesta = await fetch(url);
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    throw new Error(detalle.detail || `Error ${respuesta.status}`);
  }
  return respuesta.json();
}

function marcarConexion(ok) {
  el("estado-conexion").classList.toggle("ok", ok);
  el("estado-texto").textContent = ok ? "Conectado a la API" : "Sin conexión";
}

async function actualizarGraficos() {
  const duracion = Math.max(estado.periodos / estado.frecuencia, 0.02);
  const params = new URLSearchParams({
    frecuencia: estado.frecuencia,
    amplitud: estado.amplitud,
    duracion: duracion.toFixed(6),
    fs: estado.fs,
    armonicos: estado.armonicos,
  });

  try {
    const [senal, continuidad, espectro] = await Promise.all([
      obtenerJSON(`/senales/${estado.tipo}?${params}`),
      obtenerJSON(`/senales/${estado.tipo}/continuidad?${params}`),
      obtenerJSON(`/senales/${estado.tipo}/espectro?amplitud=${estado.amplitud}&armonicos=${estado.armonicos}`),
    ]);

    marcarConexion(true);

    const etiquetas = senal.tiempo.map((t) => redondear(t, 4));

    graficoSenal.data.labels = etiquetas;
    graficoSenal.data.datasets[0].data = senal.señal_ideal;
    graficoSenal.data.datasets[1].data = senal.señal_fourier;
    graficoSenal.update();

    graficoError.data.labels = etiquetas;
    graficoError.data.datasets[0].data = senal.error_porcentual;
    graficoError.update();

    graficoEspectro.data.labels = espectro.armonicos.map((n) => `n=${n}`);
    graficoEspectro.data.datasets[0].data = espectro.magnitud;
    graficoEspectro.update();

    // Efecto Gibbs (gibbs_analysis.error_analysis): entorno de discontinuidades.
    el("metrica-error-max").textContent = `${redondear(senal.error_maximo, 1)} %`;
    el("metrica-error-prom").textContent = `${redondear(senal.error_promedio, 1)} %`;
    el("metrica-discontinuidades").textContent = senal.cantidad_discontinuidades;

    // Tramos continuos, sin Gibbs (compation.calcular_error_continuidad).
    el("metrica-margen").textContent = `${continuidad.margen_muestras} muestras`;
    el("metrica-muestras-evaluadas").textContent = continuidad.cantidad_muestras_evaluadas;
    el("metrica-error-medio").textContent = redondear(continuidad.error_medio, 4);
    el("metrica-error-max-continuo").textContent = redondear(continuidad.error_maximo, 4);
    el("metrica-rms").textContent = redondear(continuidad.error_rms, 4);
    el("metrica-error-relativo").textContent = `${redondear(continuidad.error_relativo_medio_pct, 2)} %`;
  } catch (error) {
    marcarConexion(false);
    console.error(error);
  }
}

let temporizador = null;
function programarActualizacion() {
  clearTimeout(temporizador);
  temporizador = setTimeout(actualizarGraficos, 120);
}

function vincularSlider(idInput, idSalida, formateador = (v) => v) {
  const input = el(idInput);
  const salida = el(idSalida);

  const refrescar = () => {
    const valor = Number(input.value);
    estado[idInput] = valor;
    salida.textContent = formateador(valor);
    programarActualizacion();
  };

  input.addEventListener("input", refrescar);
  refrescar();
}

vincularSlider("frecuencia", "frecuencia-valor");
vincularSlider("amplitud", "amplitud-valor", (v) => v.toFixed(1));
vincularSlider("armonicos", "armonicos-valor");
vincularSlider("fs", "fs-valor");
vincularSlider("periodos", "periodos-valor");

el("tolerancia").addEventListener("input", (evento) => {
  estado.tolerancia = Number(evento.target.value);
  el("tolerancia-valor").textContent = estado.tolerancia.toFixed(4);
});
el("tolerancia-valor").textContent = estado.tolerancia.toFixed(4);

document.querySelectorAll(".tab").forEach((boton) => {
  boton.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("activo"));
    boton.classList.add("activo");
    estado.tipo = boton.dataset.tipo;
    el("resultado-armonicos").textContent = "";
    actualizarGraficos();
  });
});

el("boton-armonicos").addEventListener("click", async () => {
  const resultado = el("resultado-armonicos");
  resultado.textContent = "Calculando…";

  try {
    const params = new URLSearchParams({
      amplitud: estado.amplitud,
      tolerancia: estado.tolerancia,
      max_armonicos: 1000,
    });
    const datos = await obtenerJSON(`/senales/${estado.tipo}/armonicos-necesarios?${params}`);
    resultado.textContent = `${datos.armonicos_minimos} armónicos → RMS ${redondear(datos.rms_alcanzado, 4)}`;
  } catch (error) {
    resultado.textContent = `Error: ${error.message}`;
  }
});

const dropzone = el("dropzone");
const inputAudio = el("input-audio");

["dragover", "dragleave", "drop"].forEach((tipoEvento) => {
  dropzone.addEventListener(tipoEvento, (evento) => {
    evento.preventDefault();
    dropzone.classList.toggle("arrastrando", tipoEvento === "dragover");
  });
});

dropzone.addEventListener("drop", (evento) => {
  const archivo = evento.dataTransfer.files[0];
  if (archivo) importarAudio(archivo);
});

inputAudio.addEventListener("change", (evento) => {
  const archivo = evento.target.files[0];
  if (archivo) importarAudio(archivo);
});

async function importarAudio(archivo) {
  const resultado = el("resultado-audio");
  resultado.textContent = "Importando…";

  const formulario = new FormData();
  formulario.append("archivo", archivo);

  try {
    const respuesta = await fetch("/audio/importar?muestras_preview=2000", {
      method: "POST",
      body: formulario,
    });

    if (!respuesta.ok) {
      const detalle = await respuesta.json().catch(() => ({}));
      throw new Error(detalle.detail || `Error ${respuesta.status}`);
    }

    const datos = await respuesta.json();

    resultado.textContent =
      `${datos.fs} Hz · ${redondear(datos.duracion_s, 2)} s · ` +
      `${datos.cantidad_muestras.toLocaleString("es-AR")} muestras`;

    el("tarjeta-audio").classList.remove("oculto");
    graficoAudio.data.labels = datos.muestras_preview.map((_, i) => i);
    graficoAudio.data.datasets[0].data = datos.muestras_preview;
    graficoAudio.update();
  } catch (error) {
    resultado.textContent = `Error: ${error.message}`;
  }
}

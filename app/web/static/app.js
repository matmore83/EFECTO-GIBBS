const estado = {
  tipo: "pulso",
  frecuencia: 440,
  amplitud: 1,
  armonicos: 5,
  fs: 44100,
  periodos: 3,
  tolerancia: 0.001,
};

const el = (id) => document.getElementById(id);

const COLOR_IDEAL = "rgba(139, 147, 167, 0.7)";
const COLOR_FOURIER = "#7c5cff";
const COLOR_ESPECTRO = "#22d3c8";
const COLOR_FASE = "#ffb84d";
const COLOR_AUDIO = "#22d3c8";

Chart.register(ChartZoom);

Chart.defaults.color = "#8b93a7";
Chart.defaults.borderColor = "rgba(255,255,255,0.06)";
Chart.defaults.font.family = "Segoe UI, system-ui, sans-serif";

function crearGraficoLinea(ctx, datasets, opciones = {}) {
  const { plugins: pluginsExtra, scales: scalesExtra, ...resto } = opciones;

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
        ...scalesExtra,
      },
      plugins: { legend: { labels: { boxWidth: 12 } }, ...pluginsExtra },
      ...resto,
    },
  });
}

const graficoSenal = crearGraficoLinea(
  el("grafico-senal"),
  [
    { label: "Señal ideal", data: [], borderColor: COLOR_IDEAL, borderWidth: 1.5, borderDash: [4, 3] },
    { label: "Serie de Fourier", data: [], borderColor: COLOR_FOURIER, borderWidth: 2 },
  ],
  {
    plugins: {
      zoom: {
        pan: { enabled: true, mode: "x" },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: "x",
        },
        limits: { x: { min: "original", max: "original" } },
      },
    },
  }
);

const graficoEspectro = new Chart(el("grafico-espectro"), {
  data: {
    labels: [],
    datasets: [
      { type: "bar", label: "Magnitud", data: [], backgroundColor: COLOR_ESPECTRO, borderRadius: 4, yAxisID: "y" },
      {
        type: "line",
        label: "Fase (°)",
        data: [],
        borderColor: COLOR_FASE,
        borderWidth: 1.5,
        pointRadius: 2,
        pointBackgroundColor: COLOR_FASE,
        yAxisID: "y1",
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: "index", intersect: false },
    scales: {
      x: { grid: { display: false } },
      y: {
        type: "linear",
        position: "left",
        grid: { color: "rgba(255,255,255,0.04)" },
        title: { display: true, text: "Magnitud" },
      },
      y1: {
        type: "linear",
        position: "right",
        grid: { display: false },
        title: { display: true, text: "Fase (°)" },
        min: -180,
        max: 180,
      },
    },
    plugins: { legend: { display: true, labels: { boxWidth: 12 } } },
  },
});

const graficoConvergencia = crearGraficoLinea(
  el("grafico-convergencia"),
  [{ label: "RMS acumulado", data: [], borderColor: COLOR_FOURIER, borderWidth: 2, pointRadius: 0 }],
  {
    animation: { duration: 900, easing: "easeOutQuart" },
    plugins: { legend: { display: false } },
  }
);

const graficoAudio = crearGraficoLinea(el("grafico-audio"), [
  { label: "Audio importado", data: [], borderColor: COLOR_AUDIO, borderWidth: 1.2 },
]);

const graficoAudioEspectro = crearGraficoLinea(
  el("grafico-audio-espectro"),
  [{ label: "Espectro FFT", data: [], borderColor: COLOR_ESPECTRO, borderWidth: 1.2 }],
  { plugins: { legend: { display: false } } }
);

const TODOS_LOS_GRAFICOS = [graficoSenal, graficoEspectro, graficoConvergencia, graficoAudio, graficoAudioEspectro];

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

function actualizarTablaCoeficientes(coeficientes) {
  el("coef-a0").textContent = redondear(coeficientes.a0, 5);

  const cuerpo = el("tabla-coeficientes").querySelector("tbody");
  cuerpo.innerHTML = "";

  coeficientes.an.forEach((an, i) => {
    const bn = coeficientes.bn[i];
    const fila = document.createElement("tr");
    fila.innerHTML = `<td>${i + 1}</td><td>${redondear(an, 5)}</td><td>${redondear(bn, 5)}</td>`;
    cuerpo.appendChild(fila);
  });
}

async function actualizarGraficos() {
  // periodos/frecuencia mantiene siempre la misma cantidad de ciclos
  // visibles en pantalla, sin importar la frecuencia elegida.
  const duracion = Math.max(estado.periodos / estado.frecuencia, 0.0000005);
  const params = new URLSearchParams({
    frecuencia: estado.frecuencia,
    amplitud: estado.amplitud,
    duracion: duracion.toFixed(8),
    fs: estado.fs,
    armonicos: estado.armonicos,
  });

  try {
    const [senal, continuidad, espectro, coeficientes] = await Promise.all([
      obtenerJSON(`/senales/${estado.tipo}?${params}`),
      obtenerJSON(`/senales/${estado.tipo}/continuidad?${params}`),
      obtenerJSON(`/senales/${estado.tipo}/espectro?amplitud=${estado.amplitud}&armonicos=${estado.armonicos}`),
      obtenerJSON(`/senales/${estado.tipo}/coeficientes?amplitud=${estado.amplitud}&armonicos=${estado.armonicos}`),
    ]);

    marcarConexion(true);

    const etiquetas = senal.tiempo.map((t) => redondear(t, 6));

    graficoSenal.data.labels = etiquetas;
    graficoSenal.data.datasets[0].data = senal.señal_ideal;
    graficoSenal.data.datasets[1].data = senal.señal_fourier;
    graficoSenal.update();

    graficoEspectro.data.labels = espectro.armonicos.map((n) => `n=${n}`);
    graficoEspectro.data.datasets[0].data = espectro.magnitud;
    graficoEspectro.data.datasets[1].data = espectro.fase.map((rad) => (rad * 180) / Math.PI);
    graficoEspectro.update();

    actualizarTablaCoeficientes(coeficientes);

    // Efecto Gibbs (gibbs_analysis.error_analysis): entorno de discontinuidades.
    // El ~9% de sobreoscilación se mantiene constante al variar los
    // armónicos: es el comportamiento esperado del fenómeno de Gibbs.
    el("metrica-error-max").textContent = `${redondear(senal.error_maximo, 1)} %`;
    el("metrica-error-prom").textContent = `${redondear(senal.error_promedio, 1)} %`;
    el("metrica-discontinuidades").textContent = senal.cantidad_discontinuidades;

    // Tramos continuos, sin Gibbs (compation.calcular_error_continuidad).
    el("metrica-margen").textContent = `${continuidad.margen_muestras} muestras`;
    el("metrica-muestras-evaluadas").textContent = continuidad.cantidad_muestras_evaluadas;
    el("metrica-error-medio").textContent = redondear(continuidad.error_medio, 4);
    el("metrica-error-max-continuo").textContent = redondear(continuidad.error_maximo, 4);
    el("metrica-rms").textContent = redondear(continuidad.error_rms, 4);
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

function vincularFrecuencia() {
  const slider = el("frecuencia");
  const numero = el("frecuencia-numero");

  const refrescar = (valor) => {
    const acotado = Math.min(20000, Math.max(20, valor));
    estado.frecuencia = acotado;
    slider.value = acotado;
    numero.value = acotado;
    programarActualizacion();
  };

  slider.addEventListener("input", () => refrescar(Number(slider.value)));
  numero.addEventListener("change", () => refrescar(Number(numero.value) || 20));
  refrescar(Number(slider.value));
}

vincularFrecuencia();
vincularSlider("amplitud", "amplitud-valor", (v) => v.toFixed(1));
vincularSlider("armonicos", "armonicos-valor");
vincularSlider("periodos", "periodos-valor");

el("fs").addEventListener("change", (evento) => {
  estado.fs = Number(evento.target.value);
  programarActualizacion();
});
estado.fs = Number(el("fs").value);

el("tolerancia").addEventListener("input", (evento) => {
  estado.tolerancia = Number(evento.target.value);
  el("tolerancia-valor").textContent = `${(estado.tolerancia * 1e6).toFixed(2)} ×10⁻⁶`;
});
el("tolerancia-valor").textContent = `${(estado.tolerancia * 1e6).toFixed(2)} ×10⁻⁶`;

el("escala-log").addEventListener("change", (evento) => {
  graficoEspectro.options.scales.y.type = evento.target.checked ? "logarithmic" : "linear";
  graficoEspectro.update();
});

el("boton-reset-zoom").addEventListener("click", () => graficoSenal.resetZoom());

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

    const maxConvergencia = Math.min(Math.max(datos.armonicos_minimos + 10, 20), 300);
    const convergencia = await obtenerJSON(
      `/senales/${estado.tipo}/convergencia-rms?amplitud=${estado.amplitud}&max_armonicos=${maxConvergencia}`
    );

    graficoConvergencia.data.labels = convergencia.armonicos;
    graficoConvergencia.data.datasets[0].data = convergencia.rms;
    graficoConvergencia.update();
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

    el("metrica-audio-rms").textContent = redondear(datos.rms, 4);
    el("metrica-audio-pico").textContent = redondear(datos.pico, 4);

    el("tarjeta-audio").classList.remove("oculto");

    graficoAudio.data.labels = datos.muestras_preview.map((_, i) => i);
    graficoAudio.data.datasets[0].data = datos.muestras_preview;

    graficoAudioEspectro.data.labels = datos.espectro_frecuencias.map((f) => redondear(f, 0));
    graficoAudioEspectro.data.datasets[0].data = datos.espectro_magnitud;

    // Estos dos gráficos existen desde el arranque de la página dentro de
    // una tarjeta oculta (display:none, ancho 0). Chart.js necesita un
    // resize() explícito al mostrarla recién ahora; si no, el canvas queda
    // con el tamaño (inconsistente) que tenía mientras estaba oculto y el
    // próximo update() lo estira a lo ancho de forma descontrolada.
    graficoAudio.resize();
    graficoAudioEspectro.resize();
    graficoAudio.update();
    graficoAudioEspectro.update();
  } catch (error) {
    resultado.textContent = `Error: ${error.message}`;
  }
}

function coloresGrid(tema) {
  return tema === "claro" ? "rgba(0,0,0,0.08)" : "rgba(255,255,255,0.04)";
}

function aplicarTema(tema) {
  document.documentElement.setAttribute("data-tema", tema);
  el("boton-tema").textContent = tema === "claro" ? "☀️" : "🌙";
  localStorage.setItem("tema-gibbs", tema);

  Chart.defaults.color = tema === "claro" ? "#4a5164" : "#8b93a7";

  const color = coloresGrid(tema);
  TODOS_LOS_GRAFICOS.forEach((grafico) => {
    Object.values(grafico.options.scales || {}).forEach((escala) => {
      if (escala.grid && "color" in escala.grid) escala.grid.color = color;
    });
    grafico.update();
  });
}

el("boton-tema").addEventListener("click", () => {
  const actual = document.documentElement.getAttribute("data-tema") === "claro" ? "claro" : "oscuro";
  aplicarTema(actual === "claro" ? "oscuro" : "claro");
});

aplicarTema(localStorage.getItem("tema-gibbs") || "oscuro");

"""Rutas de la API para la síntesis de señales y el análisis del efecto Gibbs."""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile

from app.api.schemas import (
    MUESTRAS_MAXIMAS,
    AnalisisGibbsResponse,
    ArmonicosNecesariosParametros,
    ArmonicosNecesariosResponse,
    AudioImportadoResponse,
    ContinuidadResponse,
    ConvergenciaResponse,
    EspectroResponse,
    FourierCoefficientsResponse,
    ParametrosSenal,
)
from app.services.amplitude_vs_time import (
    generar_diente_sierra,
    generar_rectangular,
    generar_triangular,
)
from app.services.compation import (
    calcular_error_continuidad,
    calcular_margen_gibbs,
    detectar_tramos_continuidad,
)
from app.services.error_analysis import calcular_serie_rms, determinar_armonicos_rms
from app.services.fft_service import calcular_espectro_fft, calcular_estadisticos
from app.services.fourier_series import (
    coeficientes_diente_sierra,
    coeficientes_pulso,
    coeficientes_triangular,
    fourier_diente_sierra,
    fourier_pulso,
    fourier_triangular,
    magnitud_fase_diente_sierra,
    magnitud_fase_pulso,
    magnitud_fase_triangular,
)
from app.services.gibbs_analysis import error_analysis
from app.services.import_service import cargar_audio

TipoSenal = Literal["pulso", "diente-sierra", "triangular"]


@dataclass(frozen=True)
class DefinicionSenal:
    """Agrupa las funciones de servicio asociadas a un tipo de señal."""

    generar_ideal: Callable[[ParametrosSenal], np.ndarray]
    sintetizar_fourier: Callable[..., np.ndarray]
    magnitud_fase: Callable[[float, int], tuple[np.ndarray, np.ndarray]]
    coeficientes: Callable[..., tuple[float, np.ndarray, np.ndarray]]
    clave_rms: str


# Las fases iniciales (0, π, π/2) alinean cada generador "ideal" con la
# convención en seno puro (bn únicamente, sin cos) de su Serie de Fourier
# correspondiente, para que ambas curvas queden superpuestas en el
# gráfico en vez de desfasadas medio período entre sí:
# - pulso: la serie senoidal vale 0 en t=0 y sube primero -> fase=0 ya
#   coincide con el rectangular (+A para 0<tau<0.5).
# - diente de sierra: la serie senoidal vale 0 en t=0 (rampa creciente
#   centrada en el origen) -> el generador con fase=0 arranca en -A, hay
#   que correrlo medio período (fase=π) para que también valga 0 en t=0.
# - triangular: la serie senoidal sube desde 0 en t=0 hacia el pico en
#   T/4 -> el generador con fase=0 arranca en el valle (-A); un cuarto de
#   período (fase=π/2) lo alinea.
SENALES: dict[TipoSenal, DefinicionSenal] = {
    "pulso": DefinicionSenal(
        generar_ideal=lambda p: generar_rectangular(
            p.frecuencia, p.amplitud, p.duracion, p.fs, 0.0, 0.5
        ),
        sintetizar_fourier=fourier_pulso,
        magnitud_fase=magnitud_fase_pulso,
        coeficientes=coeficientes_pulso,
        clave_rms="pulso",
    ),
    "diente-sierra": DefinicionSenal(
        generar_ideal=lambda p: generar_diente_sierra(
            p.frecuencia, p.amplitud, p.duracion, p.fs, np.pi
        ),
        sintetizar_fourier=fourier_diente_sierra,
        magnitud_fase=magnitud_fase_diente_sierra,
        coeficientes=coeficientes_diente_sierra,
        clave_rms="diente_sierra",
    ),
    "triangular": DefinicionSenal(
        generar_ideal=lambda p: generar_triangular(
            p.frecuencia, p.amplitud, p.duracion, p.fs, np.pi / 2, 0.5
        ),
        sintetizar_fourier=fourier_triangular,
        magnitud_fase=magnitud_fase_triangular,
        coeficientes=coeficientes_triangular,
        clave_rms="triangular",
    ),
}

router = APIRouter(prefix="/senales", tags=["senales"])
audio_router = APIRouter(prefix="/audio", tags=["audio"])

# Cantidad máxima de puntos que se devuelven para graficar. Las métricas
# (error_maximo, error_promedio, etc.) se calculan sobre la señal completa;
# solo los arrays de graficación se recortan, para que el navegador nunca
# tenga que dibujar (ni Chart.js procesar) series de cientos de miles de
# puntos, sin importar qué combinación de fs/duración/armónicos se pida.
MAX_PUNTOS_GRAFICO = 3000


def _decimar(valores: np.ndarray, max_puntos: int = MAX_PUNTOS_GRAFICO) -> np.ndarray:
    """Recorta un array a lo sumo a `max_puntos` muestras, tomadas a paso fijo."""

    paso = max(1, len(valores) // max_puntos)

    return valores[::paso]


def _sintetizar(
    parametros: ParametrosSenal, definicion: DefinicionSenal
) -> tuple[np.ndarray, np.ndarray]:
    """Genera la señal ideal y su reconstrucción mediante Series de Fourier."""

    muestras = parametros.duracion * parametros.fs

    if muestras > MUESTRAS_MAXIMAS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"duracion * fs = {muestras:.0f} supera el máximo permitido "
                f"({MUESTRAS_MAXIMAS}). Reducí la duración o la frecuencia de muestreo."
            ),
        )

    ideal = definicion.generar_ideal(parametros)
    fourier = definicion.sintetizar_fourier(
        frecuencia=parametros.frecuencia,
        amplitud=parametros.amplitud,
        duracion=parametros.duracion,
        fs=parametros.fs,
        armonicos=parametros.armonicos,
    )

    return ideal, fourier


@router.get("/{tipo}", response_model=AnalisisGibbsResponse)
def obtener_senal(
    tipo: TipoSenal, parametros: ParametrosSenal = Depends()
) -> AnalisisGibbsResponse:
    """Sintetiza una señal mediante Series de Fourier y analiza el efecto Gibbs."""

    definicion = SENALES[tipo]
    tiempo = np.arange(0, parametros.duracion, 1 / parametros.fs)
    ideal, fourier = _sintetizar(parametros, definicion)

    # Las métricas se calculan sobre la señal a resolución completa...
    analisis = error_analysis(
        señal_ideal=ideal,
        señal_fourier=fourier,
        amplitud=parametros.amplitud,
    )

    # ...pero lo que se manda a graficar se recorta siempre al mismo tope,
    # sin importar cuántas muestras se generaron.
    return AnalisisGibbsResponse(
        tiempo=_decimar(tiempo).tolist(),
        señal_ideal=_decimar(ideal).tolist(),
        señal_fourier=_decimar(fourier).tolist(),
        error_absoluto=_decimar(analisis["error_absoluto"]).tolist(),
        error_porcentual=_decimar(analisis["error_porcentual"]).tolist(),
        indices_discontinuidad=analisis["indices_discontinuidad"].tolist(),
        error_maximo=float(analisis["error_maximo"]),
        error_promedio=float(analisis["error_promedio"]),
        cantidad_discontinuidades=int(analisis["cantidad_discontinuidades"]),
    )


@router.get("/{tipo}/espectro", response_model=EspectroResponse)
def obtener_espectro(
    tipo: TipoSenal,
    amplitud: float = 1.0,
    armonicos: int = Query(default=5, gt=0, le=500),
) -> EspectroResponse:
    """Obtiene la representación en magnitud y fase de los armónicos de una señal."""

    definicion = SENALES[tipo]
    magnitud, fase = definicion.magnitud_fase(amplitud, armonicos)

    return EspectroResponse(
        armonicos=list(range(1, armonicos + 1)),
        magnitud=magnitud.tolist(),
        fase=fase.tolist(),
    )


@router.get("/{tipo}/continuidad", response_model=ContinuidadResponse)
def obtener_continuidad(
    tipo: TipoSenal,
    parametros: ParametrosSenal = Depends(),
    factor: float = 1.0,
    umbral: float = 0.5,
) -> ContinuidadResponse:
    """Evalúa el error de reconstrucción excluyendo el entorno de las discontinuidades (efecto Gibbs)."""

    definicion = SENALES[tipo]
    ideal, fourier = _sintetizar(parametros, definicion)

    margen = calcular_margen_gibbs(
        frecuencia=parametros.frecuencia,
        fs=parametros.fs,
        armonicos=parametros.armonicos,
        factor=factor,
    )

    indices_continuidad = detectar_tramos_continuidad(ideal, margen, umbral)
    resultado = calcular_error_continuidad(ideal, fourier, indices_continuidad)

    return ContinuidadResponse(
        margen_muestras=margen,
        cantidad_muestras_evaluadas=len(resultado["indices_evaluados"]),
        error_medio=float(resultado["error_medio"]),
        error_maximo=float(resultado["error_maximo"]),
        error_rms=float(resultado["error_rms"]),
        error_relativo_medio_pct=float(resultado["error_relativo_medio_%"]),
    )


@router.get("/{tipo}/armonicos-necesarios", response_model=ArmonicosNecesariosResponse)
def obtener_armonicos_necesarios(
    tipo: TipoSenal,
    parametros: ArmonicosNecesariosParametros = Depends(),
) -> ArmonicosNecesariosResponse:
    """Determina la cantidad mínima de armónicos que satisface el criterio de convergencia RMS."""

    definicion = SENALES[tipo]

    armonicos, rms = determinar_armonicos_rms(
        tipo_senal=definicion.clave_rms,
        amplitud=parametros.amplitud,
        tolerancia=parametros.tolerancia,
        max_armonicos=parametros.max_armonicos,
    )

    return ArmonicosNecesariosResponse(
        armonicos_minimos=armonicos,
        rms_alcanzado=float(rms),
    )


@router.get("/{tipo}/convergencia-rms", response_model=ConvergenciaResponse)
def obtener_convergencia_rms(
    tipo: TipoSenal,
    amplitud: float = 1.0,
    max_armonicos: int = Query(default=60, gt=0, le=5000),
) -> ConvergenciaResponse:
    """Evolución del valor RMS acumulado para N = 1..max_armonicos armónicos."""

    definicion = SENALES[tipo]

    armonicos, rms = calcular_serie_rms(
        tipo_senal=definicion.clave_rms,
        amplitud=amplitud,
        max_armonicos=max_armonicos,
    )

    return ConvergenciaResponse(armonicos=armonicos.tolist(), rms=rms.tolist())


@audio_router.post("/importar", response_model=AudioImportadoResponse)
async def importar_audio(
    archivo: UploadFile,
    muestras_preview: int = Query(default=2000, gt=0, le=MAX_PUNTOS_GRAFICO),
) -> AudioImportadoResponse:
    """Importa un archivo de audio (.wav, .flac, .ogg, .aiff, .aif) y lo normaliza."""

    sufijo = Path(archivo.filename or "").suffix

    with tempfile.NamedTemporaryFile(suffix=sufijo, delete=False) as destino:
        destino.write(await archivo.read())
        ruta_temporal = Path(destino.name)

    try:
        señal, fs = cargar_audio(ruta_temporal)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        ruta_temporal.unlink(missing_ok=True)

    # El audio importado no tiene una expresión "ideal" con la que comparar
    # un error de reconstrucción; el equivalente del análisis que sí se hace
    # sobre las señales sintetizadas es su espectro real (FFT) y estadísticos
    # básicos de la forma de onda (RMS, pico).
    rms, pico = calcular_estadisticos(señal)
    frecuencias_fft, magnitud_fft = calcular_espectro_fft(señal, fs)

    return AudioImportadoResponse(
        fs=fs,
        cantidad_muestras=len(señal),
        duracion_s=len(señal) / fs,
        muestras_preview=señal[:muestras_preview].tolist(),
        rms=rms,
        pico=pico,
        espectro_frecuencias=frecuencias_fft.tolist(),
        espectro_magnitud=magnitud_fft.tolist(),
    )


@router.get(
    "/{tipo}/coeficientes",
    response_model=FourierCoefficientsResponse,
    summary="Coeficientes de Fourier de la señal",
    description=(
        "Calcula los coeficientes analíticos a0, an y bn de la Serie de "
        "Fourier (forma seno-coseno) usados internamente para sintetizar "
        "la señal seleccionada."
    ),
)
def obtener_coeficientes(
    tipo: TipoSenal,
    amplitud: float = 1.0,
    armonicos: int = Query(default=5, gt=0, le=500),
) -> FourierCoefficientsResponse:
    """Devuelve los coeficientes analíticos a0, an y bn de la Serie de Fourier."""

    definicion = SENALES[tipo]
    a0, an, bn = definicion.coeficientes(amplitud=amplitud, armonicos=armonicos)

    return FourierCoefficientsResponse(a0=float(a0), an=an.tolist(), bn=bn.tolist())

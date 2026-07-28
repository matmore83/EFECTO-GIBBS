"""Modelos de request/response de la API."""

from __future__ import annotations

from pydantic import BaseModel, Field

# Tope duro de muestras por señal (fs * duración). Sin este límite, un
# pedido con fs y duración altas genera arrays de cientos de miles de
# puntos: el cálculo se vuelve pesado y graficarlos tranca el navegador.
# Se valida en app.api.routes (no acá): un model_validator que falla en un
# modelo usado como dependencia de query params (Depends) no pasa por el
# manejo de errores de FastAPI y termina en un 500 en vez de un 422.
MUESTRAS_MAXIMAS = 300_000


class ParametrosSenal(BaseModel):
    """Parámetros de síntesis de una señal periódica."""

    frecuencia: float = Field(
        default=440.0,
        gt=0,
        le=20_000,
        description="Frecuencia fundamental [Hz]. Rango audible: 20 Hz - 20 kHz.",
    )
    amplitud: float = Field(default=1.0, ge=0, description="Amplitud pico.")
    duracion: float = Field(
        default=1.0, gt=0, le=10.0, description="Duración de la señal [s]."
    )
    fs: int = Field(
        default=44_100,
        gt=0,
        le=100_000,
        description="Frecuencia de muestreo [Hz]. Valores típicos: 44100, 48000.",
    )
    armonicos: int = Field(
        default=5, gt=0, le=500, description="Cantidad de armónicos."
    )


class AnalisisGibbsResponse(BaseModel):
    """Resultado de sintetizar una señal y analizar el efecto Gibbs."""

    tiempo: list[float]
    señal_ideal: list[float]
    señal_fourier: list[float]
    error_absoluto: list[float]
    error_porcentual: list[float]
    indices_discontinuidad: list[int]
    error_maximo: float
    error_promedio: float
    cantidad_discontinuidades: int


class EspectroResponse(BaseModel):
    """Representación en magnitud y fase de los armónicos de una señal."""

    armonicos: list[int]
    magnitud: list[float]
    fase: list[float]


class ContinuidadResponse(BaseModel):
    """Error de reconstrucción evaluado solo en los tramos continuos (sin Gibbs)."""

    margen_muestras: int
    cantidad_muestras_evaluadas: int
    error_medio: float
    error_maximo: float
    error_rms: float
    error_relativo_medio_pct: float


class ArmonicosNecesariosParametros(BaseModel):
    """Parámetros para determinar la cantidad mínima de armónicos por criterio RMS."""

    amplitud: float = Field(default=1.0, ge=0, description="Amplitud pico.")
    tolerancia: float = Field(
        default=0.001, gt=0, description="Error relativo máximo permitido."
    )
    max_armonicos: int = Field(
        default=500, gt=0, le=5000, description="Cantidad máxima de armónicos a probar."
    )


class ArmonicosNecesariosResponse(BaseModel):
    """Cantidad mínima de armónicos para satisfacer el criterio de convergencia RMS."""

    armonicos_minimos: int
    rms_alcanzado: float


class AudioImportadoResponse(BaseModel):
    """Resultado de importar y normalizar un archivo de audio."""

    fs: int
    cantidad_muestras: int
    duracion_s: float
    muestras_preview: list[float]
    rms: float
    pico: float
    espectro_frecuencias: list[float]
    espectro_magnitud: list[float]


class ConvergenciaResponse(BaseModel):
    """Evolución del valor RMS acumulado a medida que se agregan armónicos."""

    armonicos: list[int]
    rms: list[float]


class FourierCoefficientsResponse(BaseModel):
    """
    Coeficientes de una Serie de Fourier.
    """

    a0: float
    an: list[float]
    bn: list[float]

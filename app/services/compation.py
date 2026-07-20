"""
Cálculo del error de reconstrucción mediante Series de Fourier.

Evalúa el error únicamente en los tramos de continuidad,
excluyendo los puntos de discontinuidad.
"""

from __future__ import annotations

import numpy as np


def calcular_margen_gibbs(
    frecuencia: float,
    fs: int,
    armonicos: int,
    factor: float = 1.0,
) -> int:
    """
    Estima el margen de exclusión alrededor
    de discontinuidades debido al fenómeno de Gibbs.
    """

    tiempo_gibbs = factor / (armonicos * frecuencia)

    muestras = int(tiempo_gibbs * fs)

    return muestras


def detectar_tramos_continuidad(
    senal: np.ndarray,
    margen: int,
    umbral: float = 0.5,
) -> np.ndarray:
    """
    Obtiene los índices correspondientes a tramos continuos.

    Los puntos próximos a saltos son eliminados.

    Parámetros
    ----------
    señal:
        Señal original generada por amplitude_vs_time.

    margen:
        Cantidad de muestras eliminadas alrededor
        de cada discontinuidad.

    umbral:
        Salto mínimo para considerar discontinuidad.

    Retorna
    -------
    np.ndarray
        Índices pertenecientes a zonas continuas.
    """

    diferencia = np.abs(np.diff(senal))

    discontinuidades = np.where(diferencia > umbral)[0]

    mascara = np.ones(len(senal), dtype=bool)

    for idx in discontinuidades:
        inicio = max(0, idx - margen)

        fin = min(len(senal), idx + margen)

        mascara[inicio:fin] = False

    return np.where(mascara)[0]


def calcular_error_continuidad(
    senal_original: np.ndarray,
    senal_fourier: np.ndarray,
    indices_continuidad: np.ndarray,
) -> dict:
    """
    Calcula el error entre señal original
    y reconstrucción Fourier en regiones continuas.

    Parámetros
    ----------
    señal_original:
        Señal generada por amplitude_vs_time.

    señal_fourier:
        Señal sintetizada mediante Fourier.

    indices_continuidad:
        Índices donde se evalúa el error.

    Retorna
    -------
    dict
        Estadísticos del error.
    """

    error = senal_original[indices_continuidad] - senal_fourier[indices_continuidad]

    error_abs = np.abs(error)

    referencia = np.abs(senal_original[indices_continuidad])

    error_rel = np.zeros_like(error_abs)

    mascara = referencia > 1e-12

    error_rel[mascara] = (error_abs[mascara] / referencia[mascara]) * 100

    return {
        "error_medio": np.mean(error_abs),
        "error_maximo": np.max(error_abs),
        "error_rms": np.sqrt(np.mean(error**2)),
        "error_relativo_medio_%": np.mean(error_rel),
        "indices_evaluados": indices_continuidad,
    }

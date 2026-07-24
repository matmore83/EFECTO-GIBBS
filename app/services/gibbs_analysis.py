"""
Análisis del error entre una señal ideal y su aproximación
mediante Series de Fourier.

Este módulo permite cuantificar el error absoluto y porcentual
en el entorno de las discontinuidades, facilitando el estudio
del fenómeno de Gibbs.
"""

from __future__ import annotations

import numpy as np


def error_absoluto(
    señal_ideal: np.ndarray,
    señal_fourier: np.ndarray,
) -> np.ndarray:
    """
    Calcula el error absoluto punto a punto.

    Parámetros
    ----------
    señal_ideal : np.ndarray
        Señal ideal.

    señal_fourier : np.ndarray
        Señal sintetizada mediante Fourier.

    Retorna
    -------
    np.ndarray
        Error absoluto.
    """

    if len(señal_ideal) != len(señal_fourier):
        raise ValueError("Las señales deben tener la misma longitud.")

    return np.abs(señal_ideal - señal_fourier)


def error_porcentual(
    señal_ideal: np.ndarray,
    señal_fourier: np.ndarray,
    amplitud: float,
) -> np.ndarray:
    """
    Calcula el error porcentual respecto de la amplitud
    nominal de la señal.

    Parámetros
    ----------
    señal_ideal : np.ndarray
        Señal ideal.

    señal_fourier : np.ndarray
        Señal sintetizada.

    amplitud : float
        Amplitud pico de referencia.

    Retorna
    -------
    np.ndarray
        Error porcentual.
    """

    if amplitud <= 0:
        raise ValueError("La amplitud debe ser mayor que cero.")

    error = error_absoluto(
        señal_ideal,
        señal_fourier,
    )

    return 100 * error / amplitud


def obtener_discontinuidades(
    señal_ideal: np.ndarray,
    umbral: float | None = None,
) -> np.ndarray:
    """
    Detecta automáticamente las discontinuidades de una señal.
    """

    diferencia = np.abs(np.diff(señal_ideal))

    # Si la señal es constante, no existen discontinuidades.
    if np.max(diferencia) == 0:
        return np.array([], dtype=int)

    if umbral is None:
        umbral = 0.5 * np.max(diferencia)

    return np.where(diferencia >= umbral)[0]


def error_entorno(
    error: np.ndarray,
    indices: np.ndarray,
    ventana: int = 20,
) -> np.ndarray:
    """
    Extrae el error únicamente en el entorno
    de las discontinuidades.

    Parámetros
    ----------
    error : np.ndarray
        Error absoluto o porcentual.

    indices : np.ndarray
        Índices de discontinuidad.

    ventana : int
        Cantidad de muestras a cada lado.

    Retorna
    -------
    np.ndarray
        Error localizado alrededor de los saltos.
    """

    segmentos = []

    for indice in indices:
        inicio = max(0, indice - ventana)
        fin = min(len(error), indice + ventana + 1)

        segmentos.append(error[inicio:fin])

    if len(segmentos) == 0:
        return np.array([])

    return np.concatenate(segmentos)


def error_analysis(
    señal_ideal: np.ndarray,
    señal_fourier: np.ndarray,
    amplitud: float,
    ventana: int = 20,
) -> dict:
    """
    Analiza el error producido por la aproximación
    mediante Series de Fourier.

    Parámetros
    ----------
    señal_ideal : np.ndarray
        Señal original.

    señal_fourier : np.ndarray
        Señal sintetizada.

    amplitud : float
        Amplitud nominal.

    ventana : int
        Cantidad de muestras alrededor de cada discontinuidad.

    Retorna
    -------
    dict
        Diccionario con todas las métricas del análisis.
    """

    error_abs = error_absoluto(
        señal_ideal,
        señal_fourier,
    )

    error_pct = error_porcentual(
        señal_ideal,
        señal_fourier,
        amplitud,
    )

    discontinuidades = obtener_discontinuidades(
        señal_ideal,
    )

    entorno = error_entorno(
        error_pct,
        discontinuidades,
        ventana,
    )

    return {
        "error_absoluto": error_abs,
        "error_porcentual": error_pct,
        "indices_discontinuidad": discontinuidades,
        "error_entorno": entorno,
        "error_maximo": np.max(entorno) if entorno.size else 0.0,
        "error_promedio": np.mean(entorno) if entorno.size else 0.0,
        "cantidad_discontinuidades": len(discontinuidades),
    }

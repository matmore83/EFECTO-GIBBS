"""
Análisis espectral (FFT) de señales de audio.

A diferencia de las señales sintetizadas, un audio importado no tiene
una expresión analítica "ideal" con la que comparar el error de
reconstrucción: lo que se puede calcular es su espectro real (magnitud
por frecuencia) y estadísticos básicos de la forma de onda.
"""

from __future__ import annotations

import numpy as np


def calcular_espectro_fft(
    señal: np.ndarray,
    fs: int,
    max_puntos: int = 3000,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula el espectro de magnitud de una señal mediante FFT.

    Parámetros
    ----------
    señal : np.ndarray
        Señal en el dominio del tiempo.

    fs : int
        Frecuencia de muestreo [Hz].

    max_puntos : int
        Cantidad máxima de puntos devueltos (decimado a paso fijo).

    Retorna
    -------
    tuple[np.ndarray, np.ndarray]

        frecuencias
            Frecuencias [Hz] de cada bin (0 a fs/2).

        magnitud
            Magnitud normalizada de cada bin.
    """

    n = len(señal)

    if n == 0:
        return np.array([]), np.array([])

    espectro = np.fft.rfft(señal)
    frecuencias = np.fft.rfftfreq(n, d=1 / fs)

    magnitud = np.abs(espectro) / n * 2
    magnitud[0] /= 2  # la componente DC no se duplica

    paso = max(1, len(magnitud) // max_puntos)

    return frecuencias[::paso], magnitud[::paso]


def calcular_estadisticos(señal: np.ndarray) -> tuple[float, float]:
    """
    Calcula el valor RMS y el pico de una señal.

    Retorna
    -------
    tuple[float, float]
        rms, pico
    """

    if len(señal) == 0:
        return 0.0, 0.0

    rms = float(np.sqrt(np.mean(señal**2)))
    pico = float(np.max(np.abs(señal)))

    return rms, pico

"""
Generación de una señal diente de sierra.

"""

from __future__ import annotations

import numpy as np


def generar_diente_sierra(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    fase: float = 0,
) -> np.ndarray:
    """
    Genera una señal periódica de diente de sierra.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].
    amplitud : float
        Amplitud pico de la señal.
    duracion : float
        Duración de la señal [s].
    fs : int
        Frecuencia de muestreo [Hz].
    fase : float, opcional
        Fase inicial [rad].

    Retorna
    -------
    np.ndarray
        Vector con la señal generada.
    """

    t = np.arange(0, duracion, 1 / fs)

    # Tiempo reducido a un período
    tau = (frecuencia * t + fase / (2 * np.pi)) % 1.0

    # Diente de sierra entre -1 y 1
    y = 2.0 * tau - 1.0

    return amplitud * y


"""
Generación de una señal rectangular.

"""


def generar_rectangular(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    fase: float = np.pi,
    duty: float = 0.5,
) -> np.ndarray:
    """
    Genera una señal rectangular.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].
    amplitud : float
        Amplitud pico de la señal.
    duracion : float
        Duración de la señal [s].
    fs : int
        Frecuencia de muestreo [Hz].
    fase : float, opcional
        Fase inicial [rad].
    duty : float, opcional
        Ciclo de trabajo (0 < duty < 1).

    Retorna
    -------
    np.ndarray
        Vector con la señal generada.
    """

    if not 0.0 < duty < 1.0:
        raise ValueError("El parámetro duty debe estar comprendido entre 0 y 1.")

    t = np.arange(0, duracion, 1 / fs)

    # Fase reducida a un período
    tau = (frecuencia * t + fase / (2 * np.pi)) % 1.0

    # Señal rectangular
    y = np.where(tau < duty, amplitud, -amplitud)

    return y


"""
Generación de una señal triangular.

"""


def generar_triangular(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    fase: float = 0,
    width: float = 0.5,
) -> np.ndarray:
    """
    Genera una señal triangular.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].
    amplitud : float
        Amplitud pico de la señal.
    duracion : float
        Duración de la señal [s].
    fs : int
        Frecuencia de muestreo [Hz].
    fase : float, opcional
        Fase inicial [rad].
    width : float, opcional
        Fracción del período en la que la señal asciende
        (0 < width < 1). Para width=0.5 se obtiene una
        onda triangular simétrica.

    Retorna
    -------
    np.ndarray
        Señal triangular.
    """

    if not 0.0 < width < 1.0:
        raise ValueError("width debe estar comprendido entre 0 y 1.")

    t = np.arange(0, duracion, 1 / fs)

    # Fase reducida al intervalo [0,1)
    tau = (frecuencia * t + fase / (2 * np.pi)) % 1.0

    y = np.empty_like(tau)

    # Rampa ascendente
    asc = tau < width
    y[asc] = -1.0 + 2.0 * tau[asc] / width

    # Rampa descendente
    y[~asc] = 1.0 - 2.0 * (tau[~asc] - width) / (1.0 - width)

    return amplitud * y
